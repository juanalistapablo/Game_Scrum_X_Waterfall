"""Implementação ativa do provedor baseado na Árvore de Decisão fixa."""

from __future__ import annotations

from typing import Dict, List, Optional

from game.data.case_scrum import VITAPULSE_CASE, VITAPULSE_NODES
from game.data.case_waterfall import AEROSHIELD_CASE, AEROSHIELD_NODES
from game.models import (
    DecisionNode,
    DecisionOption,
    GameState,
    Methodology,
    ProjectCase,
)
from game.providers.base import ScenarioProvider


class StaticDecisionTreeProvider(ScenarioProvider):
    """Navega de forma determinística pelas árvores de decisão pré-estabelecidas."""

    def __init__(self) -> None:
        self._cases: Dict[str, ProjectCase] = {
            VITAPULSE_CASE.id: VITAPULSE_CASE,
            AEROSHIELD_CASE.id: AEROSHIELD_CASE,
        }
        self._nodes: Dict[str, DecisionNode] = {
            **VITAPULSE_NODES,
            **AEROSHIELD_NODES,
        }

    def list_cases(self) -> List[ProjectCase]:
        return list(self._cases.values())

    def get_case(self, case_id: str) -> ProjectCase:
        if case_id not in self._cases:
            raise KeyError(f"Case não encontrado: '{case_id}'")
        return self._cases[case_id]

    def get_node(self, node_id: str) -> DecisionNode:
        if node_id not in self._nodes:
            raise KeyError(f"Nó da árvore de decisão não encontrado: '{node_id}'")
        return self._nodes[node_id]

    def get_initial_node(self, case_id: str, methodology: Methodology) -> DecisionNode:
        case = self.get_case(case_id)
        root_id = case.root_node_ids[methodology]
        return self.get_node(root_id)

    def get_next_node(
        self,
        state: GameState,
        chosen_option: DecisionOption,
    ) -> Optional[DecisionNode]:
        if chosen_option.next_node_id is None:
            return None
        return self.get_node(chosen_option.next_node_id)

    def validate_tree_integrity(self) -> List[str]:
        """Valida se todos os root_node_ids e next_node_ids apontam para nós existentes."""
        errors: List[str] = []
        for case in self._cases.values():
            for meth, root_id in case.root_node_ids.items():
                if root_id not in self._nodes:
                    errors.append(
                        f"Case '{case.id}' ({meth.value}): nó raiz '{root_id}' inexistente."
                    )

        for node_id, node in self._nodes.items():
            if not node.options:
                errors.append(f"Nó '{node_id}' não possui opções de decisão.")
            for opt in node.options:
                if opt.next_node_id is not None and opt.next_node_id not in self._nodes:
                    errors.append(
                        f"Nó '{node_id}' opção '{opt.id}' aponta para nó inexistente '{opt.next_node_id}'."
                    )
        return errors
