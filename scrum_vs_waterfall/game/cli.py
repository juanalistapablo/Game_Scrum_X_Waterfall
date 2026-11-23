"""Interface de terminal (CLI) para jogar no terminal do VS Code.

Usa apenas a biblioteca padrão do Python (sem dependências externas).
"""

from __future__ import annotations

import textwrap
from typing import List

from game.engine import GameEngine
from game.metrics import (
    MIN_SATISFACTION_FOR_NEGOTIATION,
    NEGOTIATION_EXTRA_WEEKS,
    NEGOTIATION_SATISFACTION_COST,
)
from game.models import GameStatus, Methodology, MetricImpact, ProjectMetrics


WIDTH = 86


def _line(char: str = "=") -> str:
    return char * WIDTH


def _wrap(text: str, indent: str = "  ") -> str:
    return textwrap.fill(text, width=WIDTH - 2, initial_indent=indent, subsequent_indent=indent)


def _bar(value: int, total: int = 100, length: int = 16) -> str:
    ratio = max(0.0, min(1.0, value / max(1, total)))
    filled = round(ratio * length)
    return f"[{'#' * filled}{'-' * (length - filled)}] {value:3d}%"


def _fmt_money(amount: int) -> str:
    sign = "-" if amount < 0 else ""
    formatted = f"{abs(amount):,.0f}".replace(",", ".")
    return f"{sign}R$ {formatted}"


def _fmt_delta(value: int, suffix: str = "") -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value}{suffix}"


def _render_dashboard(
    case_name: str,
    methodology: Methodology,
    stage_name: str,
    metrics: ProjectMetrics,
    turn: int,
) -> None:
    print()
    print(_line("="))
    print(f"  PROJETO: {case_name}")
    print(f"  METODOLOGIA: {methodology.value}  |  ETAPA ATUAL: {stage_name}  |  TURNO: {turn}")
    print(_line("-"))
    print(f"  Progresso do Projeto : {_bar(metrics.progress)}")
    print(f"  Performance Técnica  : {_bar(metrics.performance)}")
    print(f"  Satisfação do Cliente: {_bar(metrics.satisfaction)}  (mín. p/ negociar prazo: {MIN_SATISFACTION_FOR_NEGOTIATION}%)")
    print(f"  Ânimo da Equipe      : {_bar(metrics.morale)}")
    print(
        f"  Orçamento Restante   : {_fmt_money(metrics.budget)} (inicial: {_fmt_money(metrics.initial_budget)})"
    )
    print(
        f"  Prazo Restante       : {metrics.deadline_weeks} semana(s) (inicial: {metrics.initial_deadline} sem.)"
    )
    print(_line("="))


def _render_impact(impact: MetricImpact, rules: List[str]) -> None:
    print("\n  IMPACTO APLICADO NESTA DECISÃO:")
    print(
        f"    Performance: {_fmt_delta(impact.performance)} | "
        f"Satisfação: {_fmt_delta(impact.satisfaction)} | "
        f"Ânimo: {_fmt_delta(impact.morale)} | "
        f"Progresso: {_fmt_delta(impact.progress, '%')}"
    )
    print(
        f"    Orçamento  : {_fmt_money(impact.budget)} | "
        f"Prazo: {_fmt_delta(impact.deadline_weeks, ' sem.')}"
    )
    if rules:
        print("  REGRAS DE CÁLCULO ATIVADAS:")
        for rule in rules:
            print(_wrap(f"- {rule}", indent="    "))


class TerminalGameUI:
    """Controlador de entrada e saída no terminal para o GameEngine."""

    def __init__(self, engine: GameEngine) -> None:
        self.engine = engine

    def run(self) -> None:
        self._print_banner()
        while True:
            case = self._select_case()
            methodology = self._select_methodology(case.name, case.description)
            self.engine.start_game(case.id, methodology)
            self._play_loop()
            self._show_final_report()

            again = input("\nDeseja jogar outro case ou testar a outra metodologia? (S/N): ").strip().upper()
            if again != "S":
                print("\nObrigado por jogar! Até a próxima gestão de projeto.\n")
                break

    def _print_banner(self) -> None:
        print()
        print(_line("="))
        print("          SCRUM vs. WATERFALL — SIMULADOR DE GERENCIAMENTO DE PROJETOS")
        print(_line("="))
        print(_wrap(
            "Neste jogo, o desafio não é apenas entregar um software: é saber como gerenciá-lo. "
            "Você receberá o briefing de um projeto robusto, escolherá entre SCRUM ou WATERFALL "
            "e tomará decisões etapa a etapa junto com sua equipe técnica."
        ))

    def _select_case(self):
        cases = self.engine.list_cases()
        print("\n" + _line("-"))
        print("  ESCOLHA O CASE DE PROJETO DE SOFTWARE:")
        print(_line("-"))
        for idx, case in enumerate(cases, start=1):
            print(f"\n  [{idx}] {case.name}")
            print(f"      {case.subtitle}")
            print(
                f"      Orçamento inicial: {_fmt_money(case.initial_metrics.budget)} | "
                f"Prazo inicial: {case.initial_metrics.deadline_weeks} semanas"
            )

        while True:
            choice = input(f"\nDigite o número do case (1-{len(cases)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(cases):
                return cases[int(choice) - 1]
            print("  Opção inválida. Tente novamente.")

    def _select_methodology(self, case_name: str, description: str) -> Methodology:
        print("\n" + _line("="))
        print(f"  BRIEFING DO CASE: {case_name}")
        print(_line("="))
        print(_wrap(description))
        print()
        print("  Qual metodologia você deseja adotar para gerenciar este projeto?")
        print("    [1] SCRUM      — Entregas iterativas em Sprints, backlog adaptável e feedback contínuo.")
        print("    [2] WATERFALL  — Fases sequenciais (Requisitos -> Projeto -> Implementação -> Teste -> Implantação -> Manutenção).")

        while True:
            choice = input("\nEscolha a metodologia (1 para SCRUM / 2 para WATERFALL): ").strip()
            if choice == "1":
                return Methodology.SCRUM
            if choice == "2":
                return Methodology.WATERFALL
            print("  Opção inválida. Digite 1 ou 2.")

    def _play_loop(self) -> None:
        assert self.engine.state is not None

        while self.engine.state.status in (
            GameStatus.IN_PROGRESS,
            GameStatus.AWAITING_DEADLINE_NEGOTIATION,
        ):
            if self.engine.state.status == GameStatus.AWAITING_DEADLINE_NEGOTIATION:
                self._handle_deadline_negotiation()
                continue

            node = self.engine.get_current_node()
            character = self.engine.get_current_character()
            assert node is not None and character is not None

            _render_dashboard(
                case_name=self.engine.state.case.name,
                methodology=self.engine.state.methodology,
                stage_name=node.stage_name,
                metrics=self.engine.state.metrics,
                turn=self.engine.state.turn + 1,
            )

            print(f"\n  EVENTO: {node.title}")
            print(_wrap(node.scenario_context))
            print()
            print(f"  {character.avatar_tag} {character.name} ({character.role}) diz:")
            print(_wrap(f'"{node.character_speech}"', indent="    "))

            print("\n  OPÇÕES DE DECISÃO:")
            valid_ids = []
            for opt in node.options:
                valid_ids.append(opt.id.upper())
                print(f"\n    [{opt.id}] {opt.label}")
                print(_wrap(opt.description, indent="        "))

            while True:
                chosen_id = input(f"\nSua decisão ({'/'.join(valid_ids)}): ").strip().upper()
                if chosen_id in valid_ids:
                    break
                print(f"  Opção inválida. Escolha entre {', '.join(valid_ids)}.")

            result = self.engine.submit_decision(chosen_id)

            print("\n" + _line("-"))
            print(f"  REAÇÃO DE {result.character.name.upper()} ({result.character.role}):")
            print(_wrap(f'"{result.chosen_option.character_reaction}"', indent="    "))
            _render_impact(result.breakdown.applied_impact, result.breakdown.applied_rules)
            print("\n  LIÇÃO DE GESTÃO:")
            print(_wrap(result.chosen_option.educational_note, indent="    "))
            print(_line("-"))

            if result.status == GameStatus.AWAITING_DEADLINE_NEGOTIATION:
                print("\n  *** ALERTA DE PRAZO ***")
                print(_wrap(result.message))
            elif result.status == GameStatus.IN_PROGRESS:
                input("\nPressione ENTER para avançar para a próxima etapa...")

    def _handle_deadline_negotiation(self) -> None:
        assert self.engine.state is not None
        m = self.engine.state.metrics
        print("\n" + _line("="))
        print("  NEGOCIAÇÃO DE EXTENSÃO DE PRAZO COM O CLIENTE")
        print(_line("="))
        print(_wrap(
            f"O prazo do projeto esgotou ({m.deadline_weeks} semanas), mas sua boa relação com "
            f"o cliente (Satisfação: {m.satisfaction}%) permite negociar uma prorrogação de "
            f"+{NEGOTIATION_EXTRA_WEEKS} semanas. O custo será {NEGOTIATION_SATISFACTION_COST}% "
            "de satisfação e 8% do orçamento inicial em despesas de extensão."
        ))
        while True:
            ans = input("\nDeseja negociar a extensão de prazo agora? (S/N): ").strip().upper()
            if ans in ("S", "N"):
                _, _, msg = self.engine.resolve_deadline_negotiation(ans == "S")
                print("\n" + _wrap(msg))
                if ans == "S":
                    input("\nPressione ENTER para retomar o projeto...")
                break
            print("  Digite S para Sim ou N para Não.")

    def _show_final_report(self) -> None:
        assert self.engine.state is not None
        report = self.engine.get_final_debriefing()
        m = self.engine.state.metrics

        print("\n" + _line("="))
        if report["status"] == GameStatus.DELIVERED:
            print("                      PROJETO ENTREGUE! RELATÓRIO FINAL")
        else:
            print("                     FIM DE JOGO — PROJETO INTERROMPIDO")
        print(_line("="))

        print(_wrap(f"Desfecho: {report['termination_reason']}"))
        print()
        print(f"  Pontuação Final      : {report['score']}/100  (Nota: {report['grade']})")
        print(_wrap(f"Veredito: {report['verdict']}"))
        print()
        print(f"  Performance Final    : {m.performance}/100")
        print(f"  Satisfação Final     : {m.satisfaction}/100")
        print(f"  Ânimo Final da Equipe: {m.morale}/100")
        print(f"  Orçamento Final      : {_fmt_money(m.budget)}")
        print(f"  Prazo Final          : {m.deadline_weeks} semana(s)")
        print(f"  Negociações de Prazo : {report['negotiations_used']}")

        print("\n" + _line("-"))
        print("  ANÁLISE METODOLÓGICA: SCRUM vs. WATERFALL NESTE CASE")
        print(_line("-"))
        fit_label = (
            "ACERTOU! Você escolheu a metodologia mais adequada para este perfil de projeto."
            if report["chose_ideal"]
            else f"DESAFIO EXTRA! Você usou {report['chosen_methodology']}, mas o ideal para este case era {report['ideal_methodology']}."
        )
        print(_wrap(fit_label))
        print("\n  Por quê?")
        print(_wrap(str(report["ideal_justification"]), indent="    "))
        print("\n  Comportamento com SCRUM:")
        print(_wrap(str(report["scrum_comparison"]), indent="    "))
        print("\n  Comportamento com WATERFALL:")
        print(_wrap(str(report["waterfall_comparison"]), indent="    "))
        print(_line("="))
