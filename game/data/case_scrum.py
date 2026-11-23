"""Case 1 (Ideal: SCRUM) — VitaPulse: Plataforma de Telemedicina, Wearables e Triagem com IA.

Contém a definição do case e duas árvores de decisão fixas completas:
- Árvore SCRUM (fluxo iterativo por Sprints com ramificações)
- Árvore WATERFALL (fluxo sequencial clássico: Requisitos -> Projeto -> Implementação -> Teste -> Implantação/Manutenção)
"""

from typing import Dict

from game.models import (
    DecisionNode,
    DecisionOption,
    Methodology,
    MetricImpact,
    ProjectCase,
    ProjectMetrics,
)


VITAPULSE_CASE = ProjectCase(
    id="vitapulse",
    name="VitaPulse — Plataforma de Telemedicina, Wearables & Triagem com IA",
    subtitle="Ecossistema HealthTech multiplataforma em mercado altamente competitivo",
    description=(
        "A HealthTech VitaPulse contratou sua equipe para construir uma plataforma robusta de "
        "telemedicina (Web + App Mobile + API de integração com smartwatches + motor de triagem "
        "assistida por IA). O mercado está em plena corrida: concorrentes lançam recursos novos "
        "todo mês, médicos e pacientes ainda estão descobrindo qual jornada funciona melhor e os "
        "investidores cobram entregas frequentes para validar o produto com usuários reais. "
        "Os requisitos de negócio têm alta chance de mudar ao longo do projeto."
    ),
    ideal_methodology=Methodology.SCRUM,
    ideal_justification=(
        "A VitaPulse tem requisitos voláteis, forte pressão de time-to-market e alta incerteza "
        "sobre a experiência ideal para médicos e pacientes. O SCRUM permite entregar incrementos "
        "funcionais a cada Sprint, coletar feedback real cedo e repriorizar o backlog sem "
        "destruir o cronograma."
    ),
    scrum_comparison=(
        "No SCRUM, mudanças de mercado são absorvidas na Sprint Planning por meio da troca de "
        "prioridades no backlog, reduzindo desperdício e mantendo o cliente engajado com demos frequentes."
    ),
    waterfall_comparison=(
        "No WATERFALL, congelar todos os requisitos no início em um mercado dinâmico gera alto "
        "risco de construir funcionalidades obsoletas ou enfrentar retrabalho caríssimo quando "
        "o cliente exige mudanças durante a Implementação e os Testes."
    ),
    initial_metrics=ProjectMetrics(
        performance=70,
        satisfaction=75,
        budget=400_000,
        initial_budget=400_000,
        deadline_weeks=16,
        initial_deadline=16,
        morale=80,
        progress=0,
    ),
    root_node_ids={
        Methodology.SCRUM: "vp_scrum_01",
        Methodology.WATERFALL: "vp_wf_01",
    },
)


VITAPULSE_NODES: Dict[str, DecisionNode] = {
    # =========================================================================
    # ÁRVORE SCRUM — VITAPULSE
    # =========================================================================
    "vp_scrum_01": DecisionNode(
        id="vp_scrum_01",
        stage_name="Sprint 0 — Descoberta & Product Backlog",
        title="Definição do MVP e Estratégia Inicial",
        character_id="ux_designer",
        character_speech=(
            "Conversei com 15 médicos e os investidores. Os investidores trouxeram 40 ideias "
            "para a primeira versão, mas os médicos dizem que só precisam de teleconsulta "
            "estável e triagem rápida para começar a usar. Como vamos estruturar o backlog?"
        ),
        scenario_context=(
            "Você precisa definir o escopo das primeiras Sprints. Aceitar tudo agora pode "
            "sobrecarregar o time, mas cortar demais sem explicar bem pode gerar ruído com o cliente."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Priorizar MVP enxuto (Teleconsulta + Triagem) e validar com 20 médicos",
                description="Aplicar MoSCoW no Product Backlog e focar valor real na Sprint 1.",
                impact=MetricImpact(
                    performance=+8,
                    satisfaction=+6,
                    budget=-55_000,
                    deadline_weeks=-2,
                    morale=+6,
                    progress=+20,
                ),
                next_node_id="vp_scrum_02_clean",
                character_reaction=(
                    "Excelente! Já montei o protótipo navegável do fluxo de triagem para "
                    "validarmos na primeira Sprint Review."
                ),
                educational_note=(
                    "No Scrum, priorizar um MVP de alto valor reduz risco de desperdício e "
                    "antecipa aprendizado real com usuários."
                ),
                tags=["mvp", "prioritization"],
            ),
            DecisionOption(
                id="B",
                label="Aceitar as 40 ideias no backlog inicial sem cortar escopo",
                description="Agradar os investidores imediatamente prometendo tudo já no começo.",
                impact=MetricImpact(
                    performance=-6,
                    satisfaction=+10,
                    budget=-85_000,
                    deadline_weeks=-3,
                    morale=-12,
                    progress=+15,
                ),
                next_node_id="vp_scrum_02_bloated",
                character_reaction=(
                    "Os investidores sorriram, mas o time já saiu da reunião assustado com o "
                    "tamanho das histórias da Sprint 1..."
                ),
                educational_note=(
                    "Aceitar escopo ilimitado sem repriorização quebra a cadência das Sprints "
                    "e cria ilusão de velocidade no início."
                ),
                tags=["scope_change", "overtime"],
            ),
            DecisionOption(
                id="C",
                label="Rodar um Spike técnico de IA antes de fechar o backlog",
                description="Investir tempo inicial para validar viabilidade do motor de triagem.",
                impact=MetricImpact(
                    performance=+12,
                    satisfaction=-3,
                    budget=-65_000,
                    deadline_weeks=-3,
                    morale=+4,
                    progress=+18,
                ),
                next_node_id="vp_scrum_02_clean",
                character_reaction=(
                    "O cliente estranhou não ver telas ainda, mas tecnicamente evitamos "
                    "armadilhas grandes no algoritmo de triagem."
                ),
                educational_note=(
                    "Spikes técnicos no Scrum reduzem incerteza arquitetural cedo, ao custo "
                    "de adiar ligeiramente a primeira entrega visível."
                ),
                tags=["quality"],
            ),
        ],
    ),
    "vp_scrum_02_clean": DecisionNode(
        id="vp_scrum_02_clean",
        stage_name="Sprint 1 — MVP Validado & Mudança de Mercado",
        title="Concorrente lança alerta de Smartwatch durante a Sprint Review",
        character_id="frontend_dev",
        character_speech=(
            "A demo da teleconsulta foi um sucesso! Mas no meio da Review o CEO viu que "
            "o principal concorrente lançou integração com smartwatch e pediu para colocarmos "
            "isso já na Sprint 2, junto com a prescrição digital que já estava planejada."
        ),
        scenario_context=(
            "Surge uma mudança clássica de mercado. Você precisa decidir como encaixar a "
            "demanda sem comprometer a sustentabilidade da Sprint 2."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Negociar troca no Backlog: entra Smartwatch, sai relatório secundário",
                description="Manter a capacidade da Sprint 2 estável trocando itens de menor valor.",
                impact=MetricImpact(
                    performance=+5,
                    satisfaction=+8,
                    budget=-75_000,
                    deadline_weeks=-3,
                    morale=+5,
                    progress=+25,
                ),
                next_node_id="vp_scrum_03_pivot",
                character_reaction=(
                    "Perfeito! Consegui focar no dashboard de batimentos sem sacrificar a "
                    "qualidade da interface de prescrição."
                ),
                educational_note=(
                    "Trocar escopo mantendo a capacidade da Sprint é uma das maiores forças "
                    "do Scrum diante de mudanças de mercado."
                ),
                tags=["negotiation", "scope_change"],
            ),
            DecisionOption(
                id="B",
                label="Aceitar o Smartwatch sem remover nada da Sprint 2",
                description="Absorver a nova funcionalidade com hora extra da equipe.",
                impact=MetricImpact(
                    performance=-10,
                    satisfaction=+4,
                    budget=-105_000,
                    deadline_weeks=-4,
                    morale=-18,
                    progress=+20,
                ),
                next_node_id="vp_scrum_03_crisis",
                character_reaction=(
                    "Estamos virando noites no front e no back. Vai sair algo, mas já "
                    "estou vendo vários bugs aparecendo na integração."
                ),
                educational_note=(
                    "Aceitar novas funcionalidades sem reorganizar o planejamento aumenta "
                    "dívida técnica, risco de atraso e desgaste da equipe."
                ),
                tags=["scope_change", "overtime"],
            ),
            DecisionOption(
                id="C",
                label="Recusar a mudança agora e adiar Smartwatch para após o lançamento",
                description="Proteger o plano original sem negociar alternativas com o cliente.",
                impact=MetricImpact(
                    performance=+6,
                    satisfaction=-14,
                    budget=-65_000,
                    deadline_weeks=-3,
                    morale=+2,
                    progress=+25,
                ),
                next_node_id="vp_scrum_03_pivot",
                character_reaction=(
                    "O código ficou limpo, mas o CEO saiu bem frustrado achando que "
                    "estamos lentos demais para reagir ao mercado."
                ),
                educational_note=(
                    "Ignorar oportunidades de mercado mesmo em ambiente ágil protege o prazo, "
                    "mas reduz o valor percebido e a satisfação do cliente."
                ),
                tags=["negotiation"],
            ),
        ],
    ),
    "vp_scrum_02_bloated": DecisionNode(
        id="vp_scrum_02_bloated",
        stage_name="Sprint 1 — Sobrecarga de Escopo",
        title="API de Triagem travada por excesso de histórias simultâneas",
        character_id="backend_dev",
        character_speech=(
            "Tentamos atacar 12 módulos ao mesmo tempo nesta Sprint. A API de triagem está "
            "lenta, metade das histórias ficou incompleta e o banco de dados já está sofrendo "
            "com consultas mal otimizadas. Precisamos agir antes da Sprint 2!"
        ),
        scenario_context=(
            "A decisão inicial de aceitar tudo no backlog cobrou o preço. Você pode frear "
            "para reorganizar o backlog ou forçar o ritmo."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Reorganizar o backlog com a PO, cortar 40% e estabilizar a API",
                description="Transparência radical com o cliente para retomar controle da entrega.",
                impact=MetricImpact(
                    performance=+10,
                    satisfaction=-6,
                    budget=-70_000,
                    deadline_weeks=-3,
                    morale=+10,
                    progress=+25,
                ),
                next_node_id="vp_scrum_03_pivot",
                character_reaction=(
                    "Ufa! Com escopo focado consegui refatorar os índices do banco e a API "
                    "voltou a responder em 120ms."
                ),
                educational_note=(
                    "A inspeção e adaptação do Scrum permitem corrigir desvios cedo, antes "
                    "que o projeto inteiro entre em colapso."
                ),
                tags=["negotiation", "quality"],
            ),
            DecisionOption(
                id="B",
                label="Manter tudo e exigir força-tarefa de fim de semana",
                description="Tentar compensar o backlog inchado com horas extras intensas.",
                impact=MetricImpact(
                    performance=-12,
                    satisfaction=-4,
                    budget=-110_000,
                    deadline_weeks=-4,
                    morale=-22,
                    progress=+18,
                ),
                next_node_id="vp_scrum_03_crisis",
                character_reaction=(
                    "A equipe está exausta. Entregamos código remendado e sem testes "
                    "unitários só para dizer que a tarefa foi fechada."
                ),
                educational_note=(
                    "Forçar horas extras contínuas reduz a moral e destrói a qualidade técnica, "
                    "criando um ciclo vicioso de retrabalho."
                ),
                tags=["overtime", "rework"],
            ),
        ],
    ),
    "vp_scrum_03_pivot": DecisionNode(
        id="vp_scrum_03_pivot",
        stage_name="Sprint 2 — Integração de Wearables & Escala",
        title="Mudança inesperada na API externa de Smartwatches",
        character_id="backend_dev",
        character_speech=(
            "O fornecedor de telemetria dos smartwatches atualizou o formato de webhook "
            "de última hora! Precisamos decidir se criamos uma camada adaptadora limpa ou "
            "fazemos um ajuste rápido direto no código principal."
        ),
        scenario_context=(
            "Uma mudança externa de dependência técnica ameaça o ritmo da Sprint 2."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Construir camada adaptadora desacoplada com testes automatizados",
                description="Proteger o núcleo do sistema contra futuras mudanças de fornecedores.",
                impact=MetricImpact(
                    performance=+12,
                    satisfaction=+4,
                    budget=-80_000,
                    deadline_weeks=-3,
                    morale=+5,
                    progress=+28,
                ),
                next_node_id="vp_scrum_04_release",
                character_reaction=(
                    "Excelente escolha arquitetural! Agora podemos plugar novos wearables "
                    "no futuro sem mexer na lógica de triagem."
                ),
                educational_note=(
                    "Excelência técnica e design limpo mantêm a agilidade sustentável nas "
                    "Sprints seguintes."
                ),
                tags=["quality"],
            ),
            DecisionOption(
                id="B",
                label="Fazer patch rápido (hardcoded) para economizar tempo nesta Sprint",
                description="Entregar rápido agora assumindo dívida técnica.",
                impact=MetricImpact(
                    performance=-8,
                    satisfaction=+6,
                    budget=-50_000,
                    deadline_weeks=-2,
                    morale=-4,
                    progress=+26,
                ),
                next_node_id="vp_scrum_04_hardening",
                character_reaction=(
                    "Funcionou na demo, mas ficou bem frágil. Se o volume de pacientes "
                    "subir, teremos que refatorar sob pressão."
                ),
                educational_note=(
                    "Atalhos técnicos aceleram o curto prazo, mas cobram juros altos na "
                    "fase de escala e lançamento."
                ),
                tags=["rework"],
            ),
        ],
    ),
    "vp_scrum_03_crisis": DecisionNode(
        id="vp_scrum_03_crisis",
        stage_name="Sprint 2 — Crise de Estabilidade & Qualidade",
        title="38 bugs críticos explodem na homologação da Teleconsulta",
        character_id="qa_engineer",
        character_speech=(
            "Nossa suíte de regressão pegou 38 bugs críticos: chamadas de vídeo caindo "
            "e prontuários duplicados! O time está no limite. Se continuarmos empurrando "
            "features novas, vamos lançar um produto quebrado."
        ),
        scenario_context=(
            "A dívida técnica acumulada transformou a Sprint 2 em uma operação de resgate."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Dedicar a Sprint para estabilização, correção de bugs e automação QA",
                description="Pausar novas features para recuperar confiabilidade e moral do time.",
                impact=MetricImpact(
                    performance=+16,
                    satisfaction=-4,
                    budget=-85_000,
                    deadline_weeks=-4,
                    morale=+12,
                    progress=+22,
                ),
                next_node_id="vp_scrum_04_hardening",
                character_reaction=(
                    "Decisão madura! Zeramos os bugs críticos e cobrimos os fluxos médicos "
                    "com testes automatizados."
                ),
                educational_note=(
                    "Parar para pagar dívida técnica dói no cronograma imediato, mas evita "
                    "um fracasso catastrófico em produção."
                ),
                tags=["quality", "rework"],
            ),
            DecisionOption(
                id="B",
                label="Corrigir apenas os bugs visíveis e continuar desenvolvendo features",
                description="Tentar esconder os problemas internos para cumprir a data.",
                impact=MetricImpact(
                    performance=-14,
                    satisfaction=-10,
                    budget=-95_000,
                    deadline_weeks=-3,
                    morale=-15,
                    progress=+24,
                ),
                next_node_id="vp_scrum_04_hardening",
                character_reaction=(
                    "Deixei registrado no relatório de risco: estamos indo para produção "
                    "com falhas sérias de integridade."
                ),
                educational_note=(
                    "Ignorar alertas de QA destrói a confiança do cliente assim que o "
                    "software entra em uso real."
                ),
                tags=["rework", "overtime"],
            ),
        ],
    ),
    "vp_scrum_04_release": DecisionNode(
        id="vp_scrum_04_release",
        stage_name="Sprint 3 — Release em Produção",
        title="Estratégia de Go-Live para 50.000 pacientes",
        character_id="devops",
        character_speech=(
            "A plataforma está estável e os testes de carga passaram! Como você quer "
            "conduzir o lançamento em produção para os hospitais parceiros?"
        ),
        scenario_context=(
            "Etapa final do projeto. Sua escolha define a segurança da entrada em produção "
            "e o fechamento dos indicadores."
        ),
        is_final_stage=True,
        options=[
            DecisionOption(
                id="A",
                label="Canary Release gradual (10% -> 50% -> 100%) com observabilidade total",
                description="Liberar em ondas com métricas em tempo real e rollback automático.",
                impact=MetricImpact(
                    performance=+10,
                    satisfaction=+10,
                    budget=-60_000,
                    deadline_weeks=-3,
                    morale=+6,
                    progress=+30,
                ),
                next_node_id=None,
                character_reaction=(
                    "Deploy impecável! Detectamos um pico de latência nos primeiros 10%, "
                    "ajustamos o autoscaling e subimos 100% sem nenhum incidente."
                ),
                educational_note=(
                    "Entregas incrementais e Canary Releases complementam perfeitamente a "
                    "filosofia ágil de redução contínua de risco."
                ),
                tags=["quality"],
            ),
            DecisionOption(
                id="B",
                label="Virada total imediata (100% no dia 1) para evento de imprensa",
                description="Economizar tempo e orçamento abrindo tudo de uma vez.",
                impact=MetricImpact(
                    performance=-6,
                    satisfaction=+6,
                    budget=-35_000,
                    deadline_weeks=-2,
                    morale=-6,
                    progress=+30,
                ),
                next_node_id=None,
                character_reaction=(
                    "Tivemos 40 minutos de lentidão no pico do lançamento, mas seguramos "
                    "a operação na raça."
                ),
                educational_note=(
                    "Mesmo em projetos bem conduzidos, um deploy Big Bang aumenta o risco "
                    "operacional na reta final."
                ),
                tags=["big_bang"],
            ),
        ],
    ),
    "vp_scrum_04_hardening": DecisionNode(
        id="vp_scrum_04_hardening",
        stage_name="Sprint 3 — Resgate & Go-Live Controlado",
        title="Lançamento sob pressão de dívida técnica",
        character_id="devops",
        character_speech=(
            "O monitoramento de staging mostra gargalos em alguns módulos secundários. "
            "Podemos subir apenas o núcleo estável com Feature Flags ou subir o pacote "
            "inteiro em uma sala de guerra no fim de semana."
        ),
        scenario_context=(
            "Etapa final sob tensão: equilibre risco operacional, prazo e expectativa do cliente."
        ),
        is_final_stage=True,
        options=[
            DecisionOption(
                id="A",
                label="Lançar núcleo estável com Feature Flags e ativar extras na semana seguinte",
                description="Proteger a experiência dos pacientes isolando módulos instáveis.",
                impact=MetricImpact(
                    performance=+8,
                    satisfaction=+4,
                    budget=-55_000,
                    deadline_weeks=-3,
                    morale=+4,
                    progress=+35,
                ),
                next_node_id=None,
                character_reaction=(
                    "Boa jogada! A teleconsulta entrou no ar estável e os médicos aprovaram "
                    "a confiabilidade do sistema."
                ),
                educational_note=(
                    "Feature Flags permitem entregas seguras mesmo após Sprints turbulentas."
                ),
                tags=["quality", "negotiation"],
            ),
            DecisionOption(
                id="B",
                label="Subir tudo junto em sala de guerra de 48h",
                description="Cumprir a promessa completa custe o que custar.",
                impact=MetricImpact(
                    performance=-12,
                    satisfaction=-8,
                    budget=-75_000,
                    deadline_weeks=-2,
                    morale=-16,
                    progress=+35,
                ),
                next_node_id=None,
                character_reaction=(
                    "O sistema ficou no ar, mas tivemos quedas durante o primeiro dia e "
                    "o time está completamente esgotado."
                ),
                educational_note=(
                    "Forçar um lançamento completo sem estabilidade compromete a reputação "
                    "do produto logo na estreia."
                ),
                tags=["overtime", "big_bang"],
            ),
        ],
    ),

    # =========================================================================
    # ÁRVORE WATERFALL — VITAPULSE (Fases clássicas: Requisitos -> Projeto ->
    # Implementação -> Teste -> Implantação & Manutenção)
    # =========================================================================
    "vp_wf_01": DecisionNode(
        id="vp_wf_01",
        stage_name="Fase 1: Requisitos (O quê)",
        title="Especificação Completa Antecipada em Mercado Volátil",
        character_id="product_owner",
        character_speech=(
            "Como escolhemos Waterfall, precisamos congelar TODOS os requisitos da "
            "VitaPulse antes de desenhar a arquitetura. Porém os médicos e investidores "
            "ainda têm dúvidas sobre o fluxo de IA e wearables. O que fazemos?"
        ),
        scenario_context=(
            "Na fase inicial do Waterfall, qualquer lacuna na especificação só costuma "
            "ser descoberta muito tarde, durante os testes ou em produção."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Investir tempo extra para fechar um documento de requisitos detalhado",
                description="Tentar prever todos os cenários antes de avançar para o Projeto.",
                impact=MetricImpact(
                    performance=+4,
                    satisfaction=-4,
                    budget=-65_000,
                    deadline_weeks=-4,
                    morale=-2,
                    progress=+18,
                ),
                next_node_id="vp_wf_02",
                character_reaction=(
                    "Conseguimos a assinatura formal do escopo, mas levamos 4 semanas sem "
                    "uma única linha de código e o mercado já começou a se mexer."
                ),
                educational_note=(
                    "Em mercados incertos, tentar congelar tudo no início consome prazo "
                    "valioso antes de qualquer validação real."
                ),
                tags=["documentation"],
            ),
            DecisionOption(
                id="B",
                label="Aprovar requisitos genéricos rapidamente para ganhar tempo",
                description="Avançar logo para a fase de Projeto deixando detalhes em aberto.",
                impact=MetricImpact(
                    performance=-8,
                    satisfaction=+4,
                    budget=-40_000,
                    deadline_weeks=-2,
                    morale=+2,
                    progress=+18,
                ),
                next_node_id="vp_wf_02",
                character_reaction=(
                    "Assinamos rápido, mas várias regras de triagem ficaram ambíguas no "
                    "documento. Isso pode voltar para nos assombrar."
                ),
                educational_note=(
                    "No Waterfall, requisitos vagos se multiplicam em retrabalho severo "
                    "nas fases de Implementação e Teste."
                ),
                tags=["rework"],
            ),
        ],
    ),
    "vp_wf_02": DecisionNode(
        id="vp_wf_02",
        stage_name="Fase 2: Projeto / Arquitetura (O quê)",
        title="Desenho Arquitetural Fechado Antes da Codificação",
        character_id="architect",
        character_speech=(
            "Terminei o diagrama completo de microsserviços, banco de dados e contratos "
            "de API com base no documento congelado. Os investidores já perguntam quando "
            "verão algo funcionando, mas ainda nem começamos a codificar."
        ),
        scenario_context=(
            "Você precisa aprovar o projeto técnico para liberar a fase de Implementação."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Aprovar arquitetura modular preparada para futuras extensões",
                description="Investir um pouco mais no desenho para amortecer mudanças futuras.",
                impact=MetricImpact(
                    performance=+10,
                    satisfaction=-6,
                    budget=-75_000,
                    deadline_weeks=-3,
                    morale=+4,
                    progress=+20,
                ),
                next_node_id="vp_wf_03_pivot",
                character_reaction=(
                    "Arquitetura sólida aprovada! Ainda não temos demo para o cliente, "
                    "mas a base técnica ficou bem estruturada."
                ),
                educational_note=(
                    "O Waterfall exige investimento pesado de projeto antes de gerar software "
                    "executável, o que testa a paciência de clientes em mercados rápidos."
                ),
                tags=["quality"],
            ),
            DecisionOption(
                id="B",
                label="Aprovar arquitetura monolítica direta para acelerar a codificação",
                description="Reduzir complexidade do projeto para tentar recuperar prazo.",
                impact=MetricImpact(
                    performance=-4,
                    satisfaction=-2,
                    budget=-55_000,
                    deadline_weeks=-2,
                    morale=-4,
                    progress=+20,
                ),
                next_node_id="vp_wf_03_pivot",
                character_reaction=(
                    "Seguimos para código mais rápido, mas qualquer alteração de escopo "
                    "vai impactar quase todos os módulos acoplados."
                ),
                educational_note=(
                    "Arquiteturas rígidas em projetos voláteis amplificam o custo de "
                    "qualquer mudança tardia."
                ),
                tags=["rework"],
            ),
        ],
    ),
    "vp_wf_03_pivot": DecisionNode(
        id="vp_wf_03_pivot",
        stage_name="Fase 3: Implementação (Como)",
        title="Choque de Mercado: Cliente exige Smartwatch no meio da codificação",
        character_id="backend_dev",
        character_speech=(
            "Estamos no meio da codificação do módulo central quando o CEO interrompeu "
            "tudo: o concorrente lançou alertas de smartwatch e ele EXIGE isso agora! "
            "No nosso modelo Waterfall, isso obriga voltar às fases de Requisitos e Projeto!"
        ),
        scenario_context=(
            "O dilema clássico do Waterfall em projetos dinâmicos: aceitar mudança tardia "
            "gera cascata de retrabalho; recusar por contrato gera forte atrito com o cliente."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Aceitar a mudança e reabrir Requisitos e Projeto (retrabalho em cascata)",
                description="Atender o pedido do CEO reescrevendo especificação, banco e APIs.",
                impact=MetricImpact(
                    performance=-6,
                    satisfaction=+8,
                    budget=-115_000,
                    deadline_weeks=-4,
                    morale=-14,
                    progress=+18,
                ),
                next_node_id="vp_wf_04",
                character_reaction=(
                    "Tivemos que jogar fora metade das rotas que já estavam prontas e "
                    "refazer o esquema de dados. O cronograma sentiu forte o golpe."
                ),
                educational_note=(
                    "No Waterfall, voltar a fases anteriores durante a Implementação tem "
                    "custo exponencial em prazo, orçamento e moral da equipe."
                ),
                tags=["scope_change", "rework"],
            ),
            DecisionOption(
                id="B",
                label="Bloquear a mudança com base no contrato congelado",
                description="Proteger cronograma e orçamento exigindo aditivo apenas na versão 2.0.",
                impact=MetricImpact(
                    performance=+4,
                    satisfaction=-22,
                    budget=-65_000,
                    deadline_weeks=-3,
                    morale=-4,
                    progress=+24,
                ),
                next_node_id="vp_wf_04",
                character_reaction=(
                    "Seguimos o plano técnico, mas o CEO disse que estamos entregando um "
                    "produto que já vai nascer atrás da concorrência."
                ),
                educational_note=(
                    "A rigidez contratual do Waterfall protege o escopo original, mas pode "
                    "destruir a satisfação do cliente quando o mercado muda."
                ),
                tags=["late_feedback"],
            ),
            DecisionOption(
                id="C",
                label="Encaixar o Smartwatch sem atualizar o Projeto (gambiarra paralela)",
                description="Tentar codar o recurso novo sem parar o cronograma oficial.",
                impact=MetricImpact(
                    performance=-16,
                    satisfaction=-4,
                    budget=-95_000,
                    deadline_weeks=-3,
                    morale=-18,
                    progress=+20,
                ),
                next_node_id="vp_wf_04",
                character_reaction=(
                    "Ficou um Frankenstein técnico. O front e o back estão dessincronizados "
                    "e os testes vão sofrer muito."
                ),
                educational_note=(
                    "Pular etapas de controle no Waterfall sem adotar práticas ágeis junta "
                    "o pior dos dois mundos: baixa previsibilidade e alta dívida técnica."
                ),
                tags=["scope_change", "rework", "overtime"],
            ),
        ],
    ),
    "vp_wf_04": DecisionNode(
        id="vp_wf_04",
        stage_name="Fase 4: Teste (Como)",
        title="Integração Tardia (Big Bang) revela falhas entre Front, Back e IA",
        character_id="qa_engineer",
        character_speech=(
            "Só agora na fase de Teste integramos Web, Mobile, Backend e IA pela primeira "
            "vez! Apareceram incompatibilidades graves de contrato e o fluxo de triagem "
            "não bate com o que os médicos esperavam."
        ),
        scenario_context=(
            "Como os testes ficaram concentrados no fim da cascata, o tempo está curto "
            "para corrigir defeitos estruturais."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Executar ciclo completo de correções e regressão antes da implantação",
                description="Garantir qualidade mesmo pressionando fortemente o prazo final.",
                impact=MetricImpact(
                    performance=+12,
                    satisfaction=-6,
                    budget=-80_000,
                    deadline_weeks=-4,
                    morale=-6,
                    progress=+22,
                ),
                next_node_id="vp_wf_05",
                character_reaction=(
                    "Conseguimos estabilizar a integração, mas o atraso na fase de testes "
                    "consumiu praticamente toda a margem do projeto."
                ),
                educational_note=(
                    "Testar apenas no final (Big Bang) concentra descobertas de bugs no "
                    "momento mais caro e apertado do cronograma."
                ),
                tags=["rework", "big_bang"],
            ),
            DecisionOption(
                id="B",
                label="Encurtar a fase de testes para tentar salvar a data de implantação",
                description="Corrigir só erros bloqueantes e deixar ajustes para a Manutenção.",
                impact=MetricImpact(
                    performance=-14,
                    satisfaction=-12,
                    budget=-45_000,
                    deadline_weeks=-2,
                    morale=-10,
                    progress=+22,
                ),
                next_node_id="vp_wf_05",
                character_reaction=(
                    "Avançamos para implantação, mas o risco de bugs chegarem aos pacientes "
                    "na estreia é altíssimo."
                ),
                educational_note=(
                    "Cortar testes no fim de um projeto Waterfall costuma transferir custos "
                    "muito maiores para a fase de Manutenção em produção."
                ),
                tags=["big_bang", "late_feedback"],
            ),
        ],
    ),
    "vp_wf_05": DecisionNode(
        id="vp_wf_05",
        stage_name="Fase 5 & 6: Implantação e Manutenção (Software em produção)",
        title="Entrega Única e Primeiro Contato Real dos Médicos",
        character_id="devops",
        character_speech=(
            "Chegamos à implantação final! Pela primeira vez os médicos vão usar o sistema "
            "completo em produção. Como devemos conduzir o Go-Live e o início da manutenção?"
        ),
        scenario_context=(
            "Etapa final da cascata: entrega em produção e transição para suporte/manutenção."
        ),
        is_final_stage=True,
        options=[
            DecisionOption(
                id="A",
                label="Implantação assistida com equipe dedicada de suporte e plano de manutenção",
                description="Alocar SRE e devs em plantão para responder rápido ao feedback tardio.",
                impact=MetricImpact(
                    performance=+6,
                    satisfaction=+6,
                    budget=-60_000,
                    deadline_weeks=-2,
                    morale=-4,
                    progress=+25,
                ),
                next_node_id=None,
                character_reaction=(
                    "Entramos em produção! Os médicos já pediram vários ajustes de usabilidade "
                    "para a fase de manutenção, mas o sistema se manteve estável."
                ),
                educational_note=(
                    "No Waterfall aplicado a produtos inovadores, muito feedback que poderia "
                    "ter sido colhido na Sprint 1 só surge após o software ir para produção."
                ),
                tags=["late_feedback"],
            ),
            DecisionOption(
                id="B",
                label="Implantação padrão sem alocação extra de suporte pós-go-live",
                description="Conter gastos finais entregando o pacote conforme contrato.",
                impact=MetricImpact(
                    performance=-8,
                    satisfaction=-12,
                    budget=-30_000,
                    deadline_weeks=-1,
                    morale=-6,
                    progress=+25,
                ),
                next_node_id=None,
                character_reaction=(
                    "O software foi entregue, mas os primeiros chamados de manutenção "
                    "acumularam rápido e desgastaram o relacionamento com o cliente."
                ),
                educational_note=(
                    "Subestimar a fase de manutenção após uma entrega única agrava o "
                    "impacto de requisitos que mudaram durante o projeto."
                ),
                tags=["big_bang", "late_feedback"],
            ),
        ],
    ),
}
