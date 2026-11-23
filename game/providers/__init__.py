"""Provedores de cenário (Árvore Estática atual e contrato pronto para API de IA)."""

from game.providers.ai_provider import AIScenarioProvider
from game.providers.base import ScenarioProvider
from game.providers.static_provider import StaticDecisionTreeProvider

__all__ = [
    "ScenarioProvider",
    "StaticDecisionTreeProvider",
    "AIScenarioProvider",
]
