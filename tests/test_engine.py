"""Testes automatizados do backend do jogo Scrum vs. Waterfall."""

import unittest

from game.characters import CHARACTERS
from game.engine import GameEngine
from game.metrics import MIN_SATISFACTION_FOR_NEGOTIATION
from game.models import GameStatus, Methodology, ProjectMetrics
from game.providers.ai_provider import AIScenarioProvider
from game.providers.static_provider import StaticDecisionTreeProvider


class TestScrumVsWaterfallBackend(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = StaticDecisionTreeProvider()
        self.engine = GameEngine(provider=self.provider)

    def test_tree_integrity_and_characters(self) -> None:
        errors = self.provider.validate_tree_integrity()
        self.assertEqual(errors, [], f"Erros na árvore de decisão: {errors}")

        # Verifica se todos os character_ids usados nos nós existem no catálogo
        for node in self.provider._nodes.values():
            self.assertIn(node.character_id, CHARACTERS)

    def test_vitapulse_scrum_full_delivery(self) -> None:
        self.engine.start_game("vitapulse", Methodology.SCRUM)
        # Caminho ótimo no Scrum: A -> A -> A -> A
        for choice in ["A", "A", "A", "A"]:
            result = self.engine.submit_decision(choice)
            if result.status == GameStatus.AWAITING_DEADLINE_NEGOTIATION:
                self.engine.resolve_deadline_negotiation(True)

        assert self.engine.state is not None
        self.assertEqual(self.engine.state.status, GameStatus.DELIVERED)
        self.assertEqual(self.engine.state.metrics.progress, 100)
        report = self.engine.get_final_debriefing()
        self.assertTrue(report["chose_ideal"])
        self.assertGreaterEqual(report["score"], 72)

    def test_vitapulse_waterfall_friction_and_delivery_or_negotiation(self) -> None:
        self.engine.start_game("vitapulse", Methodology.WATERFALL)
        # Percorre a árvore Waterfall completa (negociando prazo se necessário)
        steps = 0
        while self.engine.state and self.engine.state.status in (
            GameStatus.IN_PROGRESS,
            GameStatus.AWAITING_DEADLINE_NEGOTIATION,
        ):
            if self.engine.state.status == GameStatus.AWAITING_DEADLINE_NEGOTIATION:
                self.engine.resolve_deadline_negotiation(True)
                continue
            self.engine.submit_decision("A")
            steps += 1
            self.assertLess(steps, 20)

        assert self.engine.state is not None
        self.assertIn(
            self.engine.state.status,
            (GameStatus.DELIVERED, GameStatus.GAME_OVER_DEADLINE),
        )
        report = self.engine.get_final_debriefing()
        self.assertFalse(report["chose_ideal"])

    def test_aeroshield_waterfall_full_delivery(self) -> None:
        self.engine.start_game("aeroshield", Methodology.WATERFALL)
        for choice in ["A", "A", "A", "A", "A"]:
            result = self.engine.submit_decision(choice)
            if result.status == GameStatus.AWAITING_DEADLINE_NEGOTIATION:
                self.engine.resolve_deadline_negotiation(True)

        assert self.engine.state is not None
        self.assertEqual(self.engine.state.status, GameStatus.DELIVERED)
        report = self.engine.get_final_debriefing()
        self.assertTrue(report["chose_ideal"])
        self.assertGreaterEqual(report["score"], 80)

    def test_aeroshield_scrum_branching(self) -> None:
        self.engine.start_game("aeroshield", Methodology.SCRUM)
        # Escolhe B na Sprint 0 -> deve ramificar para nó de bloqueio de auditoria
        self.engine.submit_decision("B")
        node = self.engine.get_current_node()
        assert node is not None
        self.assertEqual(node.id, "as_scrum_02_audit")

    def test_deadline_game_over_when_satisfaction_too_low(self) -> None:
        self.engine.start_game("vitapulse", Methodology.WATERFALL)
        assert self.engine.state is not None
        # Simula prazo quase esgotado e satisfação abaixo do limite de negociação
        self.engine.state.metrics = ProjectMetrics(
            performance=60,
            satisfaction=MIN_SATISFACTION_FOR_NEGOTIATION - 20,
            budget=100_000,
            initial_budget=400_000,
            deadline_weeks=1,
            initial_deadline=16,
            morale=60,
            progress=20,
        )
        result = self.engine.submit_decision("A")
        self.assertEqual(result.status, GameStatus.GAME_OVER_DEADLINE)

    def test_deadline_negotiation_when_satisfaction_sufficient(self) -> None:
        self.engine.start_game("vitapulse", Methodology.SCRUM)
        assert self.engine.state is not None
        self.engine.state.metrics = ProjectMetrics(
            performance=75,
            satisfaction=MIN_SATISFACTION_FOR_NEGOTIATION + 15,
            budget=200_000,
            initial_budget=400_000,
            deadline_weeks=1,
            initial_deadline=16,
            morale=75,
            progress=20,
        )
        result = self.engine.submit_decision("A")
        self.assertEqual(result.status, GameStatus.AWAITING_DEADLINE_NEGOTIATION)
        status, impact, _ = self.engine.resolve_deadline_negotiation(True)
        self.assertEqual(status, GameStatus.IN_PROGRESS)
        self.assertIsNotNone(impact)
        self.assertEqual(self.engine.state.negotiations_used, 1)

    def test_ai_provider_contract_ready(self) -> None:
        ai_provider = AIScenarioProvider(api_key="test")
        self.assertEqual(len(ai_provider.list_cases()), 2)
        node = ai_provider.get_initial_node("vitapulse", Methodology.SCRUM)
        self.assertEqual(node.id, "vp_scrum_01")


if __name__ == "__main__":
    unittest.main()
