"""Servidor Web local em Python puro para rodar a interface 2D no VS Code ou navegador.

Zero dependências externas (usa apenas http.server + json da biblioteca padrão).
Como executar:
    python web_server.py
Depois abra http://127.0.0.1:8000 no navegador ou no Simple Browser do VS Code.
"""

from __future__ import annotations

import json
import mimetypes
import os
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from game.characters import CHARACTERS
from game.engine import GameEngine
from game.metrics import (
    MIN_SATISFACTION_FOR_NEGOTIATION,
    NEGOTIATION_BUDGET_PENALTY_RATE,
    NEGOTIATION_EXTRA_WEEKS,
    NEGOTIATION_SATISFACTION_COST,
)
from game.models import DecisionNode, GameStatus, Methodology, MetricImpact, ProjectMetrics
from game.providers.static_provider import StaticDecisionTreeProvider


WEB_DIR = Path(__file__).resolve().parent / "web"

# Mapa explícito de etapas para a visualização 2D de cada metodologia
WATERFALL_STAGES = [
    {"index": 0, "id": "requisitos", "label": "Requisitos", "group": "O quê"},
    {"index": 1, "id": "projeto", "label": "Projeto", "group": "O quê"},
    {"index": 2, "id": "implementacao", "label": "Implementação", "group": "Como"},
    {"index": 3, "id": "teste", "label": "Teste", "group": "Como"},
    {"index": 4, "id": "implantacao", "label": "Implantação", "group": "Software em produção"},
    {"index": 5, "id": "manutencao", "label": "Manutenção", "group": "Software em produção"},
]

SCRUM_STAGES = [
    {"index": 0, "id": "sprint_0", "label": "Sprint 0", "subtitle": "Discovery & Backlog"},
    {"index": 1, "id": "sprint_1", "label": "Sprint 1", "subtitle": "MVP & Feedback"},
    {"index": 2, "id": "sprint_2", "label": "Sprint 2", "subtitle": "Evolução & Integração"},
    {"index": 3, "id": "sprint_3", "label": "Sprint 3", "subtitle": "Hardening & Escala"},
    {"index": 4, "id": "release", "label": "Release", "subtitle": "Entrega em Produção"},
]


def _serialize_metrics(m: ProjectMetrics) -> Dict[str, Any]:
    return {
        "performance": m.performance,
        "satisfaction": m.satisfaction,
        "budget": m.budget,
        "initial_budget": m.initial_budget,
        "deadline_weeks": m.deadline_weeks,
        "initial_deadline": m.initial_deadline,
        "morale": m.morale,
        "progress": m.progress,
    }


def _serialize_impact(imp: MetricImpact) -> Dict[str, Any]:
    return {
        "performance": imp.performance,
        "satisfaction": imp.satisfaction,
        "budget": imp.budget,
        "deadline_weeks": imp.deadline_weeks,
        "morale": imp.morale,
        "progress": imp.progress,
    }


def _infer_stage_index(node: DecisionNode, methodology: Methodology) -> int:
    """Infere o índice visual da etapa a partir do stage_index ou nome da etapa."""
    if node.stage_index > 0:
        return node.stage_index
    text = node.stage_name.lower()
    if methodology == Methodology.WATERFALL:
        if "requisito" in text:
            return 0
        if "projeto" in text or "arquitetura" in text:
            return 1
        if "implementa" in text:
            return 2
        if "teste" in text:
            return 3
        if "manuten" in text and "implanta" not in text:
            return 5
        if "implanta" in text:
            return 4
        return 0
    else:
        if "sprint 0" in text:
            return 0
        if "sprint 1" in text:
            return 1
        if "sprint 2" in text:
            return 2
        if "sprint 3" in text and "release" not in text and "go-live" not in text:
            return 3
        if "release" in text or "go-live" in text or "final" in text:
            return 4
        return 0


def _infer_rollback_stage(
    node: DecisionNode,
    option_tags: list[str],
    explicit_rollback: Optional[int],
    methodology: Methodology,
) -> Optional[int]:
    """Determina para qual etapa da cascata houve retorno em caso de erro/retrabalho."""
    if methodology != Methodology.WATERFALL:
        return None
    if explicit_rollback is not None:
        return explicit_rollback

    current_idx = _infer_stage_index(node, methodology)
    tags = set(option_tags)
    if current_idx == 0:
        return None
    if "scope_change" in tags:
        return 0  # Mudança de escopo no Waterfall obriga voltar para Requisitos
    if "rework" in tags:
        return max(0, current_idx - 1)  # Retrabalho volta para a etapa anterior na cascata
    if "big_bang" in tags and current_idx >= 3:
        return 2  # Erro de integração tardia volta para Implementação
    return None


def _infer_mood(impact: MetricImpact, explicit_mood: str) -> str:
    if explicit_mood != "neutral":
        return explicit_mood
    score = impact.performance + impact.satisfaction + impact.morale
    if score >= 8:
        return "happy"
    if score <= -8:
        return "worried"
    return "neutral"


class GameSessionStore:
    """Mantém a instância ativa do GameEngine em memória para o servidor local."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.engine = GameEngine(provider=StaticDecisionTreeProvider())
        self.last_event: Optional[Dict[str, Any]] = None

    def get_cases_payload(self) -> Dict[str, Any]:
        cases = []
        for c in self.engine.list_cases():
            cases.append(
                {
                    "id": c.id,
                    "name": c.name,
                    "subtitle": c.subtitle,
                    "description": c.description,
                    "initial_metrics": _serialize_metrics(c.initial_metrics),
                }
            )
        return {
            "cases": cases,
            "characters": [
                {
                    "id": ch.id,
                    "name": ch.name,
                    "role": ch.role,
                    "specialty": ch.specialty,
                    "avatar_tag": ch.avatar_tag,
                }
                for ch in CHARACTERS.values()
            ],
            "config": {
                "min_satisfaction_for_negotiation": MIN_SATISFACTION_FOR_NEGOTIATION,
                "negotiation_extra_weeks": NEGOTIATION_EXTRA_WEEKS,
                "negotiation_satisfaction_cost": NEGOTIATION_SATISFACTION_COST,
                "negotiation_budget_penalty_rate": NEGOTIATION_BUDGET_PENALTY_RATE,
            },
        }

    def start_game(self, case_id: str, methodology_str: str) -> Dict[str, Any]:
        with self._lock:
            methodology = Methodology(methodology_str.upper())
            self.engine.start_game(case_id, methodology)
            self.last_event = None
            return self._build_state_payload()

    def submit_decision(self, option_id: str) -> Dict[str, Any]:
        with self._lock:
            prev_node = self.engine.get_current_node()
            assert prev_node is not None and self.engine.state is not None
            methodology = self.engine.state.methodology
            prev_stage_index = _infer_stage_index(prev_node, methodology)

            result = self.engine.submit_decision(option_id)
            rollback_to = _infer_rollback_stage(
                prev_node,
                result.chosen_option.tags,
                result.chosen_option.rollback_to_stage,
                methodology,
            )
            mood = _infer_mood(
                result.breakdown.applied_impact,
                result.chosen_option.reaction_mood,
            )

            self.last_event = {
                "character": {
                    "id": result.character.id,
                    "name": result.character.name,
                    "role": result.character.role,
                    "avatar_tag": result.character.avatar_tag,
                },
                "option_id": result.chosen_option.id,
                "option_label": result.chosen_option.label,
                "character_reaction": result.chosen_option.character_reaction,
                "educational_note": result.chosen_option.educational_note,
                "mood": mood,
                "applied_impact": _serialize_impact(result.breakdown.applied_impact),
                "applied_rules": result.breakdown.applied_rules,
                "message": result.message,
                "from_stage_index": prev_stage_index,
                "rollback_to_stage": rollback_to,
                "tags": result.chosen_option.tags,
            }
            return self._build_state_payload()

    def resolve_negotiation(self, accept: bool) -> Dict[str, Any]:
        with self._lock:
            status, impact, message = self.engine.resolve_deadline_negotiation(accept)
            self.last_event = {
                "negotiation": True,
                "accepted": accept,
                "status": status.value,
                "applied_impact": _serialize_impact(impact) if impact else None,
                "message": message,
            }
            return self._build_state_payload()

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return self._build_state_payload()

    def _build_state_payload(self) -> Dict[str, Any]:
        state = self.engine.state
        if state is None:
            return {"active": False}

        node = self.engine.get_current_node()
        char = self.engine.get_current_character()
        methodology = state.methodology

        current_stage_index = (
            _infer_stage_index(node, methodology)
            if node is not None
            else (5 if methodology == Methodology.WATERFALL else 4)
        )

        node_payload = None
        if node is not None and char is not None:
            node_payload = {
                "id": node.id,
                "stage_name": node.stage_name,
                "stage_index": current_stage_index,
                "title": node.title,
                "scenario_context": node.scenario_context,
                "character_speech": node.character_speech,
                "is_final_stage": node.is_final_stage,
                "character": {
                    "id": char.id,
                    "name": char.name,
                    "role": char.role,
                    "specialty": char.specialty,
                    "avatar_tag": char.avatar_tag,
                },
                "options": [
                    {
                        "id": opt.id,
                        "label": opt.label,
                        "description": opt.description,
                        "tags": opt.tags,
                        "may_rollback": (
                            _infer_rollback_stage(
                                node, opt.tags, opt.rollback_to_stage, methodology
                            )
                            is not None
                        ),
                    }
                    for opt in node.options
                ],
            }

        debriefing = None
        if state.status in (
            GameStatus.DELIVERED,
            GameStatus.GAME_OVER_DEADLINE,
            GameStatus.GAME_OVER_SATISFACTION,
            GameStatus.GAME_OVER_MORALE,
        ):
            raw = self.engine.get_final_debriefing()
            debriefing = {
                **raw,
                "status": state.status.value,
            }

        return {
            "active": True,
            "case": {
                "id": state.case.id,
                "name": state.case.name,
                "subtitle": state.case.subtitle,
                "description": state.case.description,
            },
            "methodology": methodology.value,
            "stages": WATERFALL_STAGES if methodology == Methodology.WATERFALL else SCRUM_STAGES,
            "current_stage_index": current_stage_index,
            "status": state.status.value,
            "turn": state.turn,
            "negotiations_used": state.negotiations_used,
            "max_negotiations": state.max_negotiations,
            "termination_reason": state.termination_reason,
            "metrics": _serialize_metrics(state.metrics),
            "current_node": node_payload,
            "last_event": self.last_event,
            "history": [
                {
                    "turn": rec.turn,
                    "stage_name": rec.stage_name,
                    "character_name": rec.character_name,
                    "character_role": rec.character_role,
                    "option_id": rec.option_id,
                    "option_label": rec.option_label,
                    "educational_note": rec.educational_note,
                }
                for rec in state.history
            ],
            "debriefing": debriefing,
        }


def create_handler(store: GameSessionStore):
    class GameRequestHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            # Mantém o terminal limpo durante o jogo
            return

        def _send_json(self, payload: Dict[str, Any], status: int = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> Dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            return json.loads(raw.decode("utf-8"))

        def _serve_static(self, rel_path: str) -> None:
            clean = rel_path.lstrip("/") or "index.html"
            target = (WEB_DIR / clean).resolve()
            if not str(target).startswith(str(WEB_DIR.resolve())) or not target.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "Arquivo não encontrado")
                return
            mime, _ = mimetypes.guess_type(str(target))
            data = target.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", f"{mime or 'application/octet-stream'}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path == "/api/cases":
                self._send_json(store.get_cases_payload())
            elif path == "/api/state":
                self._send_json(store.get_state())
            else:
                self._serve_static(path)

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            try:
                body = self._read_json()
                if path == "/api/start":
                    payload = store.start_game(body["case_id"], body["methodology"])
                    self._send_json(payload)
                elif path == "/api/decide":
                    payload = store.submit_decision(body["option_id"])
                    self._send_json(payload)
                elif path == "/api/negotiate":
                    payload = store.resolve_negotiation(bool(body.get("accept", False)))
                    self._send_json(payload)
                else:
                    self._send_json({"error": "Rota não encontrada"}, HTTPStatus.NOT_FOUND)
            except (KeyError, ValueError, RuntimeError) as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    return GameRequestHandler


def run_server(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> None:
    store = GameSessionStore()
    server = ThreadingHTTPServer((host, port), create_handler(store))
    url = f"http://{host}:{port}"
    print("=" * 72)
    print("  SCRUM vs. WATERFALL — INTERFACE 2D LOCAL")
    print("=" * 72)
    print(f"  Servidor ativo em: {url}")
    print("  Dica no VS Code : Ctrl+Shift+P -> 'Simple Browser: Show' -> cole a URL acima")
    print("  Para encerrar   : Ctrl+C neste terminal")
    print("=" * 72)
    if open_browser and not os.environ.get("NO_BROWSER"):
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
