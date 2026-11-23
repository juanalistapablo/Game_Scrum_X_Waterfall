"""Testes de integração da API HTTP local e da visualização de cascata/Scrum."""

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

from web_server import GameSessionStore, create_handler


class TestWebServerAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.store = GameSessionStore()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(self.store))
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def _get(self, path: str):
        with urlopen(f"http://127.0.0.1:{self.port}{path}") as resp:
            return resp.status, resp.read()

    def _post_json(self, path: str, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_static_index_and_cases_endpoint(self) -> None:
        status, html = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"Scrum", html)

        status, raw = self._get("/api/cases")
        self.assertEqual(status, 200)
        data = json.loads(raw.decode("utf-8"))
        self.assertEqual(len(data["cases"]), 2)
        self.assertEqual(len(data["characters"]), 7)

    def test_waterfall_rollback_signal_on_scope_change(self) -> None:
        # Inicia VitaPulse em Waterfall e avança até a Fase 3 (Implementação)
        status, state = self._post_json("/api/start", {"case_id": "vitapulse", "methodology": "WATERFALL"})
        self.assertEqual(status, 200)
        self.assertEqual(state["current_stage_index"], 0)

        # Fase 1 -> Fase 2
        _, state = self._post_json("/api/decide", {"option_id": "A"})
        self.assertEqual(state["current_stage_index"], 1)

        # Fase 2 -> Fase 3 (Implementação)
        _, state = self._post_json("/api/decide", {"option_id": "A"})
        self.assertEqual(state["current_stage_index"], 2)

        # Fase 3: escolher A (aceitar mudança de escopo) deve sinalizar retorno para Requisitos (stage 0)
        _, state = self._post_json("/api/decide", {"option_id": "A"})
        self.assertEqual(state["last_event"]["from_stage_index"], 2)
        self.assertEqual(state["last_event"]["rollback_to_stage"], 0)

    def test_scrum_flow_via_http(self) -> None:
        status, state = self._post_json("/api/start", {"case_id": "vitapulse", "methodology": "SCRUM"})
        self.assertEqual(status, 200)
        self.assertEqual(state["methodology"], "SCRUM")
        self.assertEqual(len(state["stages"]), 5)

        for choice in ["A", "A", "A", "A"]:
            _, state = self._post_json("/api/decide", {"option_id": choice})
            if state["status"] == "AWAITING_DEADLINE_NEGOTIATION":
                _, state = self._post_json("/api/negotiate", {"accept": True})

        self.assertEqual(state["status"], "DELIVERED")
        self.assertIsNotNone(state["debriefing"])
        self.assertTrue(state["debriefing"]["chose_ideal"])


if __name__ == "__main__":
    unittest.main()
