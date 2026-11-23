"""Motor principal do jogo (GameEngine), 100% desacoplado de interface (CLI/Web).

Gerencia:
- Início de partida (escolha de case + metodologia)
- Consulta ao nó atual e personagem responsável
- Aplicação de decisões e cálculo de métricas
- Verificação de condições de término e mecânica de negociação de prazo
- Geração do debriefing educativo final
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from game.characters import get_character
from game.metrics import MIN_SATISFACTION_FOR_NEGOTIATION, MetricsCalculator
from game.models import (
    Character,
    DecisionNode,
    DecisionRecord,
    GameState,
    GameStatus,
    Methodology,
    MetricImpact,
    ProjectCase,
    TurnResult,
)
from game.providers.base import ScenarioProvider
from game.providers.static_provider import StaticDecisionTreeProvider


class GameEngine:
    """Orquestrador de regras do jogo Scrum vs. Waterfall."""

    def __init__(
        self,
        provider: Optional[ScenarioProvider] = None,
        calculator: Optional[MetricsCalculator] = None,
    ) -> None:
        self.provider: ScenarioProvider = provider or StaticDecisionTreeProvider()
        self.calculator: MetricsCalculator = calculator or MetricsCalculator()
        self.state: Optional[GameState] = None
        self._current_node: Optional[DecisionNode] = None

    def list_cases(self) -> List[ProjectCase]:
        return self.provider.list_cases()

    def start_game(self, case_id: str, methodology: Methodology) -> GameState:
        case = self.provider.get_case(case_id)
        root_node = self.provider.get_initial_node(case_id, methodology)
        self._current_node = root_node
        self.state = GameState(
            case=case,
            methodology=methodology,
            metrics=case.initial_metrics,
            current_node_id=root_node.id,
            status=GameStatus.IN_PROGRESS,
        )
        return self.state

    def get_current_node(self) -> Optional[DecisionNode]:
        return self._current_node

    def get_current_character(self) -> Optional[Character]:
        if self._current_node is None:
            return None
        return get_character(self._current_node.character_id)

    def submit_decision(self, option_id: str) -> TurnResult:
        if self.state is None or self._current_node is None:
            raise RuntimeError("Nenhuma partida ativa ou nó atual disponível.")
        if self.state.status != GameStatus.IN_PROGRESS:
            raise RuntimeError(
                f"Não é possível tomar decisão no estado atual: {self.state.status.value}"
            )

        option_map = {opt.id.upper(): opt for opt in self._current_node.options}
        key = option_id.strip().upper()
        if key not in option_map:
            raise ValueError(f"Opção inválida: '{option_id}'. Opções: {list(option_map.keys())}")

        chosen = option_map[key]
        character = get_character(self._current_node.character_id)

        new_metrics, breakdown = self.calculator.calculate(
            case=self.state.case,
            methodology=self.state.methodology,
            current=self.state.metrics,
            option=chosen,
        )

        self.state.turn += 1
        self.state.metrics = new_metrics
        self.state.history.append(
            DecisionRecord(
                turn=self.state.turn,
                node_id=self._current_node.id,
                stage_name=self._current_node.stage_name,
                character_name=character.name,
                character_role=character.role,
                option_id=chosen.id,
                option_label=chosen.label,
                breakdown=breakdown,
                educational_note=chosen.educational_note,
            )
        )

        next_node = self.provider.get_next_node(self.state, chosen)
        self._current_node = next_node
        self.state.current_node_id = next_node.id if next_node else None

        # Avaliar condições de término e negociação de prazo
        message = self._evaluate_state_transition(next_node)

        return TurnResult(
            state=self.state,
            chosen_option=chosen,
            character=character,
            breakdown=breakdown,
            status=self.state.status,
            message=message,
        )

    def _evaluate_state_transition(self, next_node: Optional[DecisionNode]) -> str:
        assert self.state is not None
        m = self.state.metrics

        # 1. Colapso de satisfação do cliente
        if m.satisfaction <= 0:
            self.state.status = GameStatus.GAME_OVER_SATISFACTION
            self.state.termination_reason = (
                "A satisfação do cliente chegou a 0%. O cliente perdeu completamente a "
                "confiança na gestão e rescindiu o contrato."
            )
            return self.state.termination_reason

        # 2. Colapso de ânimo da equipe
        if m.morale <= 0:
            self.state.status = GameStatus.GAME_OVER_MORALE
            self.state.termination_reason = (
                "O ânimo da equipe chegou a 0%. Desenvolvedores-chave pediram desligamento "
                "e o projeto ficou inviável."
            )
            return self.state.termination_reason

        # 3. Se chegou ao fim da árvore (entrega concluída)
        if next_node is None:
            # Se o prazo estourou exatamente na última etapa sem chance de entrega no prazo
            if m.deadline_weeks < 0 and not self.calculator.can_negotiate_deadline(
                m, self.state.negotiations_used, self.state.max_negotiations
            ):
                self.state.status = GameStatus.GAME_OVER_DEADLINE
                self.state.termination_reason = (
                    f"O prazo esgotou na reta final ({m.deadline_weeks} sem.) e a satisfação "
                    f"do cliente ({m.satisfaction}% < {MIN_SATISFACTION_FOR_NEGOTIATION}%) "
                    "não permitiu negociar prorrogação. O contrato foi encerrado."
                )
                return self.state.termination_reason

            # Projeto entregue com sucesso!
            self.state.metrics = self.state.metrics.__class__(
                performance=m.performance,
                satisfaction=m.satisfaction,
                budget=m.budget,
                initial_budget=m.initial_budget,
                deadline_weeks=m.deadline_weeks,
                initial_deadline=m.initial_deadline,
                morale=m.morale,
                progress=100,
            )
            self.state.status = GameStatus.DELIVERED
            self.state.termination_reason = "Projeto entregue em produção!"
            return self.state.termination_reason

        # 4. Prazo acabou antes de finalizar o projeto -> checar negociação
        if m.deadline_weeks <= 0:
            if self.calculator.can_negotiate_deadline(
                m, self.state.negotiations_used, self.state.max_negotiations
            ):
                self.state.status = GameStatus.AWAITING_DEADLINE_NEGOTIATION
                return (
                    f"ATENÇÃO: O prazo chegou a {m.deadline_weeks} semanas! Porém, como a "
                    f"satisfação do cliente está em {m.satisfaction}% (>= {MIN_SATISFACTION_FOR_NEGOTIATION}%), "
                    "você pode tentar negociar uma extensão de prazo."
                )
            else:
                self.state.status = GameStatus.GAME_OVER_DEADLINE
                self.state.termination_reason = (
                    f"O prazo terminou ({m.deadline_weeks} sem.) e a satisfação do cliente "
                    f"({m.satisfaction}%) está abaixo do mínimo ({MIN_SATISFACTION_FOR_NEGOTIATION}%) "
                    "ou o limite de negociações foi atingido. O cliente recusou prorrogar o prazo!"
                )
                return self.state.termination_reason

        self.state.status = GameStatus.IN_PROGRESS
        return "Etapa concluída. Avançando para a próxima fase do projeto."

    def resolve_deadline_negotiation(self, accept_negotiation: bool) -> Tuple[GameStatus, Optional[MetricImpact], str]:
        """Processa a escolha do jogador quando o prazo acabou e o cliente aceita negociar."""
        if self.state is None:
            raise RuntimeError("Nenhuma partida ativa.")
        if self.state.status != GameStatus.AWAITING_DEADLINE_NEGOTIATION:
            raise RuntimeError("Não há negociação de prazo pendente.")

        if not accept_negotiation:
            self.state.status = GameStatus.GAME_OVER_DEADLINE
            self.state.termination_reason = (
                "Você optou por não negociar extensão de prazo. O projeto foi encerrado por atraso."
            )
            return self.state.status, None, self.state.termination_reason

        new_metrics, impact = self.calculator.apply_deadline_negotiation(self.state.metrics)
        self.state.metrics = new_metrics
        self.state.negotiations_used += 1
        self.state.status = GameStatus.IN_PROGRESS
        return (
            self.state.status,
            impact,
            (
                f"Negociação aceita! Você ganhou +{impact.deadline_weeks} semanas de prazo "
                f"(satisfação {impact.satisfaction}%, custo R$ {abs(impact.budget):,.0f})."
            ),
        )

    def get_final_debriefing(self) -> Dict[str, object]:
        """Monta o relatório pedagógico final comparando Scrum vs. Waterfall no case jogado."""
        if self.state is None:
            raise RuntimeError("Nenhuma partida ativa.")

        score, grade, verdict = self.calculator.evaluate_final_score(self.state.metrics)
        chose_ideal = self.state.methodology == self.state.case.ideal_methodology

        return {
            "status": self.state.status,
            "termination_reason": self.state.termination_reason,
            "score": score,
            "grade": grade,
            "verdict": verdict,
            "chosen_methodology": self.state.methodology.value,
            "ideal_methodology": self.state.case.ideal_methodology.value,
            "chose_ideal": chose_ideal,
            "ideal_justification": self.state.case.ideal_justification,
            "scrum_comparison": self.state.case.scrum_comparison,
            "waterfall_comparison": self.state.case.waterfall_comparison,
            "negotiations_used": self.state.negotiations_used,
            "lessons": [rec.educational_note for rec in self.state.history],
        }
