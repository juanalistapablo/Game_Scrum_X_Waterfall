# Scrum vs. Waterfall — Simulador 2D Local (VS Code)

Simulador educativo de gerenciamento de projetos de software em **Python puro + HTML/CSS/JS** (zero dependências externas). Roda tanto na **interface 2D Web local** (dentro do *Simple Browser* do VS Code ou no navegador) quanto no **terminal**.

## Como rodar a Interface 2D sem sair do VS Code

1. Extraia o arquivo ZIP e abra a pasta `scrum_vs_waterfall` no VS Code.
2. No terminal do VS Code (`Ctrl + '`), execute:

```bash
python web_server.py
```

3. O jogo abrirá em `http://127.0.0.1:8000`. Para jogar **dentro do próprio VS Code**:
   - Pressione `Ctrl + Shift + P`
   - Digite **Simple Browser: Show**
   - Cole `http://127.0.0.1:8000` e pressione **Enter**

*(Para jogar no modo terminal clássico, rode `python main.py`.)*

## Como rodar os testes automatizados

```bash
python -m unittest discover -s tests -v
```

## O que foi incluído na Interface 2D

- **Tela inicial**: escolha entre os 2 cases (**VitaPulse** — ideal Scrum; **AeroShield ATC** — ideal Waterfall), leitura do briefing completo e escolha da metodologia.
- **Tela fixa de jogo**: HUD superior com barras animadas de Progresso, Performance, Satisfação, Ânimo, Orçamento e Prazo.
- **Visualização específica da metodologia**:
  - **Waterfall**: diagrama 2D em cascata (*O quê: Requisitos/Projeto* → *Como: Implementação/Teste* → *Software em produção: Implantação/Manutenção*). O marcador desce a cascata conforme o projeto avança e **sobe de volta pela seta tracejada de retorno** até a etapa do erro quando uma decisão gera retrabalho ou mudança de escopo.
  - **Scrum**: visualizador do ciclo iterativo das Sprints (*Planning → Build → Review → Retro*) e mini-quadro Kanban de incrementos.
- **Palco 2D com personagens ao lado das decisões**: 7 personagens técnicos com sprites 2D em SVG, animação de entrada, balão de diálogo e reação facial (`happy`, `neutral`, `worried`).
- **Modularização pronta para API de IA**: basta implementar `get_next_node()` em `game/providers/ai_provider.py` e trocar o provedor no `GameEngine`.
