"""Esqueleto modular para futura integração com API de IA (ex.: Gemini / OpenAI).

Como plugar no futuro sem alterar o GameEngine nem a CLI:
1. Implemente `_call_llm_api(prompt)` usando o SDK da API de IA escolhida.
2. Retorne JSON no formato definido em `EXPECTED_NODE_SCHEMA`.
3. Passe `AIScenarioProvider(api_key=...)` ao instanciar `GameEngine(provider=...)` em `main.py`.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from game.characters import CHARACTERS
from game.models import (
    DecisionNode,
    DecisionOption,
    GameState,
    Methodology,
    MetricImpact,
    ProjectCase,
)
from game.providers.base import ScenarioProvider
from game.providers.static_provider import StaticDecisionTreeProvider


EXPECTED_NODE_SCHEMA: Dict[str, Any] = {
    "id": "string",
    "stage_name": "string",
    "title": "string",
    "character_id": list(CHARACTERS.keys()),
    "character_speech": "string",
    "scenario_context": "string",
    "is_final_stage": "bool",
    "options": [
        {
            "id": "A",
            "label": "string",
            "description": "string",
            "impact": {
                "performance": 0,
                "satisfaction": 0,
                "budget": -50000,
                "deadline_weeks": -2,
                "morale": 0,
                "progress": 20,
            },
            "next_node_id": "string ou null (null finaliza o projeto)",
            "character_reaction": "string",
            "educational_note": "string",
            "tags": ["scope_change", "quality", "rework", "negotiation"],
        }
    ],
}


class AIScenarioProvider(ScenarioProvider):
    """Provedor preparado para gerar cenários dinâmicos via API de IA.

    Por padrão, reutiliza os cases base do StaticDecisionTreeProvider e permite
    sobrescrever apenas a geração de nós (`get_next_node`).
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash") -> None:
        self.api_key = api_key
        self.model_name = model_name
        self._fallback = StaticDecisionTreeProvider()

    def list_cases(self) -> List[ProjectCase]:
        return self._fallback.list_cases()

    def get_case(self, case_id: str) -> ProjectCase:
        return self._fallback.get_case(case_id)

    def get_initial_node(self, case_id: str, methodology: Methodology) -> DecisionNode:
        return self._fallback.get_initial_node(case_id, methodology)

    def build_prompt(self, state: GameState, chosen_option: DecisionOption) -> str:
        """Monta o prompt estruturado com histórico, métricas e schema JSON esperado."""
        payload = {
            "case": state.case.name,
            "methodology": state.methodology.value,
            "ideal_methodology": state.case.ideal_methodology.value,
            "turn": state.turn,
            "metrics": {
                "performance": state.metrics.performance,
                "satisfaction": state.metrics.satisfaction,
                "budget": state.metrics.budget,
                "deadline_weeks": state.metrics.deadline_weeks,
                "morale": state.metrics.morale,
                "progress": state.metrics.progress,
            },
            "last_decision": chosen_option.label,
            "available_characters": list(CHARACTERS.keys()),
            "output_schema": EXPECTED_NODE_SCHEMA,
        }
        return (
            "Você é o mestre de um jogo educativo de Gerenciamento de Projetos (Scrum vs Waterfall). "
            "Gere o próximo nó de decisão em JSON válido seguindo exatamente output_schema:\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)
        )

    def parse_node_from_json(self, raw_json: str) -> DecisionNode:
        """Converte a resposta JSON da API de IA em um DecisionNode tipado."""
        data = json.loads(raw_json)
        options = [
            DecisionOption(
                id=opt["id"],
                label=opt["label"],
                description=opt["description"],
                impact=MetricImpact(**opt["impact"]),
                next_node_id=opt.get("next_node_id"),
                character_reaction=opt["character_reaction"],
                educational_note=opt["educational_note"],
                tags=opt.get("tags", []),
            )
            for opt in data["options"]
        ]
        return DecisionNode(
            id=data["id"],
            stage_name=data["stage_name"],
            title=data["title"],
            character_id=data["character_id"],
            character_speech=data["character_speech"],
            scenario_context=data["scenario_context"],
            options=options,
            is_final_stage=bool(data.get("is_final_stage", False)),
        )

    def get_next_node(
        self,
        state: GameState,
        chosen_option: DecisionOption,
    ) -> Optional[DecisionNode]:
        raise NotImplementedError(
            "AIScenarioProvider é um módulo pronto para integração futura. "
            "Conecte sua API de IA aqui chamando `self.build_prompt(state, chosen_option)` "
            "e convertendo a resposta com `self.parse_node_from_json(response_text)`."
        )
