"""Ponto de entrada do jogo Scrum vs. Waterfall (execução no terminal do VS Code).

Como rodar:
    python main.py
"""

from game.cli import TerminalGameUI
from game.engine import GameEngine
from game.providers.static_provider import StaticDecisionTreeProvider


def main() -> None:
    # Para trocar por uma API de IA no futuro, basta substituir o provider abaixo
    # por AIScenarioProvider(api_key="SUA_CHAVE") sem alterar o GameEngine nem a CLI.
    provider = StaticDecisionTreeProvider()
    engine = GameEngine(provider=provider)
    ui = TerminalGameUI(engine=engine)
    ui.run()


if __name__ == "__main__":
    main()
