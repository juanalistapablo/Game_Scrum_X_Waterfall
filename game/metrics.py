"""Motor matemático de cálculo de métricas e regras de negociação de prazo.

Regras implementadas:
1. Aderência Metodológica (Scrum vs. Waterfall em relação ao case):
   - Quando a metodologia escolhida é compatível com o case, ganhos alinhados
     são reforçados e penalidades operacionais são amortecidas.
   - Quando é incompatível, eventos críticos ligados às fragilidades daquela
     metodologia (ex.: mudança de escopo no Waterfall ou burocracia/auditoria
     no Scrum) amplificam custos, atrasos e queda de performance.
2. Efeito do Ânimo da Equipe:
   - Moral baixa (< 40) reduz ganhos de performance e progresso e agrava atrasos
     em decisões com hora extra ou retrabalho.
   - Moral alta (>= 80) potencializa ganhos de performance técnica.
3. Pressão de Orçamento:
   - Operar com orçamento negativo penaliza satisfação do cliente e moral.
4. Regra de Negociação de Prazo:
   - Se o prazo zerar antes da entrega, o cliente só aceita negociar uma
     extensão se sua satisfação estiver >= MIN_SATISFACTION_FOR_NEGOTIATION.
"""

from __future__ import annotations

from typing import List, Tuple

from game.models import (
    DecisionOption,
    ImpactBreakdown,
    Methodology,
    MetricImpact,
    ProjectCase,
    ProjectMetrics,
)


MIN_SATISFACTION_FOR_NEGOTIATION = 55
NEGOTIATION_EXTRA_WEEKS = 4
NEGOTIATION_SATISFACTION_COST = -15
NEGOTIATION_BUDGET_PENALTY_RATE = 0.08  # 8% do orçamento inicial em custos de extensão


def _clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, value))


class MetricsCalculator:
    """Calcula ajustes de métricas a cada decisão de forma transparente e auditável."""

    def calculate(
        self,
        case: ProjectCase,
        methodology: Methodology,
        current: ProjectMetrics,
        option: DecisionOption,
    ) -> Tuple[ProjectMetrics, ImpactBreakdown]:
        base = option.impact
        tags = set(option.tags)
        rules: List[str] = []

        perf = base.performance
        sat = base.satisfaction
        bud = base.budget
        dead = base.deadline_weeks
        mor = base.morale
        prog = base.progress

        is_ideal = methodology == case.ideal_methodology

        # 1. Multiplicador de Aderência Metodológica
        if is_ideal:
            if perf > 0:
                perf = round(perf * 1.15)
            if dead < 0 and "rework" not in tags:
                # Metodologia adequada absorve melhor impactos operacionais
                dead = min(-1, round(dead * 0.85)) if dead <= -3 else dead
            if bud < 0:
                bud = round(bud * 0.90)
            rules.append(
                f"Aderência positiva ({methodology.value} adequado ao case): custos reduzidos em 10% e ganhos técnicos +15%."
            )
        else:
            # Penalidades específicas da metodologia inadequada
            friction_tags = set()
            if methodology == Methodology.WATERFALL:
                friction_tags = {"scope_change", "rework", "late_feedback", "big_bang"}
            else:
                friction_tags = {"compliance", "audit", "documentation", "certification"}

            if tags & friction_tags:
                if bud < 0:
                    bud = round(bud * 1.35)
                if dead < 0:
                    dead = round(dead * 1.35)
                if perf < 0:
                    perf = round(perf * 1.25)
                if sat < 0:
                    sat = round(sat * 1.20)
                rules.append(
                    f"Atrito metodológico ({methodology.value} em case ideal para {case.ideal_methodology.value}): "
                    f"retrabalho/rigidez amplificou custos e prazos em ~35%."
                )
            else:
                if bud < 0:
                    bud = round(bud * 1.10)
                rules.append(
                    f"Desalinhamento leve ({methodology.value} não é o ideal para este case): sobrecarga de +10% nos custos."
                )

        # 2. Efeito do Ânimo da Equipe
        if current.morale < 40:
            if perf > 0:
                perf = round(perf * 0.70)
            if prog > 0:
                prog = max(5, round(prog * 0.80))
            if tags & {"overtime", "rework"}:
                dead -= 1
            rules.append(
                "Equipe desgastada (ânimo < 40): produtividade técnica reduzida e maior risco de atraso."
            )
        elif current.morale >= 80:
            if perf > 0:
                perf = round(perf * 1.15)
            rules.append(
                "Equipe altamente engajada (ânimo >= 80): bônus de +15% no ganho de performance."
            )

        # 3. Pressão de Estouro de Orçamento
        projected_budget = current.budget + bud
        if projected_budget < 0:
            sat -= 6
            mor -= 4
            rules.append(
                "Estouro de orçamento (saldo negativo): pressão extra de -6 na satisfação do cliente e -4 no ânimo."
            )

        applied = MetricImpact(
            performance=perf,
            satisfaction=sat,
            budget=bud,
            deadline_weeks=dead,
            morale=mor,
            progress=prog,
        )

        new_metrics = ProjectMetrics(
            performance=_clamp(current.performance + applied.performance, 0, 100),
            satisfaction=_clamp(current.satisfaction + applied.satisfaction, 0, 100),
            budget=current.budget + applied.budget,
            initial_budget=current.initial_budget,
            deadline_weeks=current.deadline_weeks + applied.deadline_weeks,
            initial_deadline=current.initial_deadline,
            morale=_clamp(current.morale + applied.morale, 0, 100),
            progress=_clamp(current.progress + applied.progress, 0, 100),
        )

        breakdown = ImpactBreakdown(
            base_impact=base,
            applied_impact=applied,
            applied_rules=rules,
        )
        return new_metrics, breakdown

    def can_negotiate_deadline(
        self,
        metrics: ProjectMetrics,
        negotiations_used: int,
        max_negotiations: int,
    ) -> bool:
        """Verifica se a satisfação do cliente permite negociar extensão de prazo."""
        return (
            negotiations_used < max_negotiations
            and metrics.satisfaction >= MIN_SATISFACTION_FOR_NEGOTIATION
        )

    def apply_deadline_negotiation(
        self, metrics: ProjectMetrics
    ) -> Tuple[ProjectMetrics, MetricImpact]:
        """Aplica extensão de prazo negociada com o cliente."""
        budget_cost = -round(metrics.initial_budget * NEGOTIATION_BUDGET_PENALTY_RATE)
        impact = MetricImpact(
            performance=0,
            satisfaction=NEGOTIATION_SATISFACTION_COST,
            budget=budget_cost,
            deadline_weeks=NEGOTIATION_EXTRA_WEEKS,
            morale=-3,
            progress=0,
        )
        new_metrics = ProjectMetrics(
            performance=metrics.performance,
            satisfaction=_clamp(metrics.satisfaction + impact.satisfaction, 0, 100),
            budget=metrics.budget + impact.budget,
            initial_budget=metrics.initial_budget,
            deadline_weeks=max(1, metrics.deadline_weeks + impact.deadline_weeks),
            initial_deadline=metrics.initial_deadline,
            morale=_clamp(metrics.morale + impact.morale, 0, 100),
            progress=metrics.progress,
        )
        return new_metrics, impact

    def evaluate_final_score(self, metrics: ProjectMetrics) -> Tuple[int, str, str]:
        """Calcula pontuação final (0-100), nota (S/A/B/C/D) e veredito."""
        budget_ratio = max(0.0, min(1.0, metrics.budget / max(1, metrics.initial_budget)))
        budget_score = round(budget_ratio * 100) if metrics.budget >= 0 else 0
        deadline_score = 100 if metrics.deadline_weeks >= 2 else (75 if metrics.deadline_weeks >= 0 else 30)

        score = round(
            metrics.performance * 0.30
            + metrics.satisfaction * 0.30
            + metrics.morale * 0.20
            + budget_score * 0.10
            + deadline_score * 0.10
        )

        if score >= 85:
            return score, "S", "Entrega Exemplar — equilíbrio excelente entre valor, qualidade, prazo e equipe."
        if score >= 72:
            return score, "A", "Entrega Sólida — projeto bem gerenciado com pequenos trade-offs controlados."
        if score >= 58:
            return score, "B", "Entrega Aceitável — o software foi entregue, mas houve desgaste perceptível."
        if score >= 45:
            return score, "C", "Entrega Crítica — entregue no limite, com dívida técnica ou desgaste elevado."
        return score, "D", "Entrega Frágil — projeto chegou ao fim com sérios problemas de sustentabilidade."
