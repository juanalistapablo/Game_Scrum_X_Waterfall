"""Contrato abstrato para provedores de cenários e árvore de decisão.

Esta abstração garante desacoplamento total entre o motor do jogo (GameEngine)
e a origem dos nós de decisão:
- Hoje: StaticDecisionTreeProvider (árvores fixas pré-estabelecidas)
- Futuro: AIScenarioProvider (geração dinâmica via API de LLM mantendo o mesmo contrato)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from game.models import (
    DecisionNode,
    DecisionOption,
    GameState,
    Methodology,
    ProjectCase,
)


class ScenarioProvider(ABC):
    """Interface padrão que qualquer fonte de cenários (estática ou IA) deve implementar."""

    @abstractmethod
    def list_cases(self) -> List[ProjectCase]:
        """Retorna todos os cases de projeto disponíveis."""

    @abstractmethod
    def get_case(self, case_id: str) -> ProjectCase:
        """Retorna um case específico pelo ID."""

    @abstractmethod
    def get_initial_node(self, case_id: str, methodology: Methodology) -> DecisionNode:
        """Retorna o nó raiz da árvore de decisão para o case e metodologia escolhidos."""

    @abstractmethod
    def get_next_node(
        self,
        state: GameState,
        chosen_option: DecisionOption,
    ) -> Optional[DecisionNode]:
        """Retorna o próximo nó da árvore de decisão ou None se o projeto terminou."""
