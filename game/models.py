"""Modelos de domínio do jogo Scrum vs. Waterfall.

Todas as estruturas são imutáveis ou tipadas com dataclasses para facilitar
serialização em JSON, testes unitários e futura integração com APIs REST ou IA.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Methodology(str, Enum):
    SCRUM = "SCRUM"
    WATERFALL = "WATERFALL"


class GameStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_DEADLINE_NEGOTIATION = "AWAITING_DEADLINE_NEGOTIATION"
    DELIVERED = "DELIVERED"
    GAME_OVER_DEADLINE = "GAME_OVER_DEADLINE"
    GAME_OVER_SATISFACTION = "GAME_OVER_SATISFACTION"
    GAME_OVER_MORALE = "GAME_OVER_MORALE"


@dataclass(frozen=True)
class Character:
    """Representa um membro da equipe que traz demandas e reage às decisões."""

    id: str
    name: str
    role: str
    specialty: str
    avatar_tag: str


@dataclass(frozen=True)
class MetricImpact:
    """Impacto base de uma decisão antes dos modificadores dinâmicos."""

    performance: int = 0
    satisfaction: int = 0
    budget: int = 0          # Em Reais (negativo = gasto, positivo = economia)
    deadline_weeks: int = 0  # Em semanas (negativo = consumo/atraso, positivo = ganho)
    morale: int = 0
    progress: int = 0        # Em pontos percentuais (0 a 100)


@dataclass(frozen=True)
class DecisionOption:
    """Alternativa de decisão dentro de um nó da árvore."""

    id: str
    label: str
    description: str
    impact: MetricImpact
    next_node_id: Optional[str]  # None indica que esta escolha conclui o projeto
    character_reaction: str
    educational_note: str
    tags: List[str] = field(default_factory=list)
    rollback_to_stage: Optional[int] = None  # No Waterfall: etapa (0-5) para onde a cascata retorna em caso de erro/retrabalho
    reaction_mood: str = "neutral"           # "happy", "neutral", "worried" para animação 2D do personagem


@dataclass(frozen=True)
class DecisionNode:
    """Nó da árvore de decisão representando uma etapa/evento do projeto."""

    id: str
    stage_name: str          # Ex.: "Fase 1: Requisitos" ou "Sprint 1: MVP"
    title: str
    character_id: str        # Personagem que aciona o gerente nesta etapa
    character_speech: str    # Fala direta do personagem trazendo a demanda
    scenario_context: str    # Situação técnica/de negócio apresentada na tela
    options: List[DecisionOption]
    is_final_stage: bool = False
    stage_index: int = 0     # Waterfall: 0=Requisitos..5=Manutenção | Scrum: 0=Sprint 0..4=Release


@dataclass(frozen=True)
class ProjectMetrics:
    """Estado atual dos indicadores do projeto."""

    performance: int         # 0 a 100
    satisfaction: int        # 0 a 100
    budget: int              # Valor restante em Reais (pode ficar negativo = estouro)
    initial_budget: int
    deadline_weeks: int      # Semanas restantes
    initial_deadline: int
    morale: int              # 0 a 100
    progress: int            # 0 a 100


@dataclass(frozen=True)
class ProjectCase:
    """Definição de um case de projeto de software."""

    id: str
    name: str
    subtitle: str
    description: str
    ideal_methodology: Methodology
    ideal_justification: str
    waterfall_comparison: str
    scrum_comparison: str
    initial_metrics: ProjectMetrics
    root_node_ids: Dict[Methodology, str]


@dataclass(frozen=True)
class ImpactBreakdown:
    """Detalhamento transparente de como os deltas foram calculados."""

    base_impact: MetricImpact
    applied_impact: MetricImpact
    applied_rules: List[str]


@dataclass(frozen=True)
class DecisionRecord:
    """Registro histórico de uma decisão tomada pelo jogador."""

    turn: int
    node_id: str
    stage_name: str
    character_name: str
    character_role: str
    option_id: str
    option_label: str
    breakdown: ImpactBreakdown
    educational_note: str


@dataclass
class GameState:
    """Estado completo da partida atual."""

    case: ProjectCase
    methodology: Methodology
    metrics: ProjectMetrics
    current_node_id: Optional[str]
    status: GameStatus = GameStatus.IN_PROGRESS
    turn: int = 0
    negotiations_used: int = 0
    max_negotiations: int = 2
    history: List[DecisionRecord] = field(default_factory=list)
    termination_reason: str = ""


@dataclass(frozen=True)
class TurnResult:
    """Retorno estruturado após processar uma decisão do jogador."""

    state: GameState
    chosen_option: DecisionOption
    character: Character
    breakdown: ImpactBreakdown
    status: GameStatus
    message: str
