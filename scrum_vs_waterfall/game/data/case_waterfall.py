"""Case 2 (Ideal: WATERFALL) — AeroShield ATC: Sistema Crítico de Controle de Tráfego Aéreo.

Contém a definição do case e duas árvores de decisão fixas completas:
- Árvore WATERFALL (fluxo sequencial clássico: Requisitos -> Projeto -> Implementação -> Teste -> Implantação/Manutenção)
- Árvore SCRUM (fluxo iterativo enfrentando exigências regulatórias, auditoria e certificação)
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


AEROSHIELD_CASE = ProjectCase(
    id="aeroshield",
    name="AeroShield ATC — Sistema Crítico de Controle de Tráfego Aéreo",
    subtitle="Software de missão crítica com certificação aeronáutica (DO-178C)",
    description=(
        "A Autoridade de Aviação Civil contratou sua engenharia para desenvolver o AeroShield ATC, "
        "um software crítico que processa telemetria de radares, prevenção de colisões e "
        "consoles de operadores de torre em tempo real. TODOS os requisitos técnicos, protocolos "
        "de hardware, critérios de redundância e normas de segurança (DO-178C) já estão "
        "rigidamente especificados em contrato. Cada etapa exige aprovação formal de auditores "
        "(Gate Review) antes de avançar, e nenhum módulo pode ir para produção sem certificação completa."
    ),
    ideal_methodology=Methodology.WATERFALL,
    ideal_justification=(
        "O AeroShield ATC possui requisitos 100% claros, estáveis e regulados por lei, altíssima "
        "criticidade (vidas em risco) e exigência de rastreabilidade documental completa antes "
        "de cada fase. O WATERFALL oferece governança rigorosa, arquitetura fechada validada "
        "antecipadamente e aderência natural a auditorias e certificações."
    ),
    waterfall_comparison=(
        "No WATERFALL, cada fase (Requisitos -> Projeto -> Implementação -> Teste -> Implantação "
        "-> Manutenção) gera os artefatos formais exigidos pelos auditores, evitando retrabalho "
        "documental e garantindo rastreabilidade ponta a ponta."
    ),
    scrum_comparison=(
        "No SCRUM, tentar entregar incrementos parciais em um ambiente onde nada entra em "
        "produção sem certificação completa gera atrito constante com auditores, retrabalho "
        "de documentação a cada Sprint e risco de reprovação em homologação."
    ),
    initial_metrics=ProjectMetrics(
        performance=75,
        satisfaction=70,
        budget=1_200_000,
        initial_budget=1_200_000,
        deadline_weeks=24,
        initial_deadline=24,
        morale=75,
        progress=0,
    ),
    root_node_ids={
        Methodology.WATERFALL: "as_wf_01",
        Methodology.SCRUM: "as_scrum_01",
    },
)


AEROSHIELD_NODES: Dict[str, DecisionNode] = {
    # =========================================================================
    # ÁRVORE WATERFALL — AEROSHIELD ATC (Ideal)
    # =========================================================================
    "as_wf_01": DecisionNode(
        id="as_wf_01",
        stage_name="Fase 1: Requisitos & Conformidade (O quê)",
        title="Baseline de Requisitos e Matriz de Rastreabilidade DO-178C",
        character_id="product_owner",
        character_speech=(
            "Recebemos o caderno técnico da autoridade aeronáutica com 320 requisitos "
            "obrigatórios de segurança e latência máxima de 50ms. Os auditores exigem "
            "uma matriz de rastreabilidade formal assinada antes de liberarem o Projeto."
        ),
        scenario_context=(
            "No Waterfall aplicado a sistemas críticos, a qualidade da Fase 1 define "
            "a estabilidade de todo o restante da cascata."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Concluir matriz de rastreabilidade completa e aprovação formal (Gate 1)",
                description="Revisar os 320 requisitos com auditores e congelar a baseline.",
                impact=MetricImpact(
                    performance=+10,
                    satisfaction=+10,
                    budget=-180_000,
                    deadline_weeks=-4,
                    morale=+5,
                    progress=+20,
                ),
                next_node_id="as_wf_02_solid",
                character_reaction=(
                    "Gate 1 aprovado sem ressalvas! Os auditores elogiaram o rigor e "
                    "temos clareza absoluta para o arquiteto desenhar o sistema."
                ),
                educational_note=(
                    "Quando os requisitos são estáveis e regulados, investir tempo na "
                    "especificação inicial elimina ambiguidades caras nas fases seguintes."
                ),
                tags=["compliance", "documentation"],
            ),
            DecisionOption(
                id="B",
                label="Aprovar baseline parcial para começar a arquitetura 2 semanas antes",
                description="Deixar 15% dos requisitos de contingência para detalhar depois.",
                impact=MetricImpact(
                    performance=-8,
                    satisfaction=-6,
                    budget=-120_000,
                    deadline_weeks=-2,
                    morale=-4,
                    progress=+16,
                ),
                next_node_id="as_wf_02_rushed",
                character_reaction=(
                    "O auditor registrou uma pendência condicional. Avançamos mais cedo, "
                    "mas qualquer lacuna nos requisitos de falha pode travar a certificação."
                ),
                educational_note=(
                    "Pular rigor na Fase 1 do Waterfall compromete a maior vantagem do "
                    "modelo: previsibilidade e conformidade."
                ),
                tags=["rework"],
            ),
        ],
    ),
    "as_wf_02_solid": DecisionNode(
        id="as_wf_02_solid",
        stage_name="Fase 2: Projeto / Arquitetura (O quê)",
        title="Arquitetura de Alta Disponibilidade e Redundância Ativo-Ativo",
        character_id="architect",
        character_speech=(
            "Com os requisitos fechados, projetei uma arquitetura redundante com failover "
            "em menos de 20ms entre servidores primário e secundário. Preciso decidir "
            "se validamos o desenho com simulação formal antes de codificar."
        ),
        scenario_context=(
            "A Fase 2 fecha 'o quê' e prepara 'como' o sistema será implementado."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Realizar revisão formal de arquitetura + simulação de falhas (Gate 2)",
                description="Validar matematicamente tolerância a falhas antes da implementação.",
                impact=MetricImpact(
                    performance=+12,
                    satisfaction=+8,
                    budget=-200_000,
                    deadline_weeks=-4,
                    morale=+6,
                    progress=+20,
                ),
                next_node_id="as_wf_03",
                character_reaction=(
                    "Encontramos um potencial deadlock no failover ainda no papel! "
                    "Corrigir isso agora custou 10x menos do que corrigir em código."
                ),
                educational_note=(
                    "Detectar defeitos de arquitetura na fase de Projeto é o ponto mais "
                    "econômico do ciclo de vida em sistemas críticos."
                ),
                tags=["quality", "compliance"],
            ),
            DecisionOption(
                id="B",
                label="Aprovar arquitetura direto sem simulação para economizar orçamento",
                description="Confiar na experiência do arquiteto e seguir para codificação.",
                impact=MetricImpact(
                    performance=-4,
                    satisfaction=-2,
                    budget=-130_000,
                    deadline_weeks=-3,
                    morale=-2,
                    progress=+20,
                ),
                next_node_id="as_wf_03",
                character_reaction=(
                    "Seguimos para implementação, mas sem a simulação formal vamos ter "
                    "que provar a tolerância a falhas na marra durante os testes."
                ),
                educational_note=(
                    "Em sistemas críticos, economizar na verificação de projeto eleva o "
                    "risco de reprovação na etapa de testes formais."
                ),
                tags=["rework"],
            ),
        ],
    ),
    "as_wf_02_rushed": DecisionNode(
        id="as_wf_02_rushed",
        stage_name="Fase 2: Projeto sob Pendência Regulatória (O quê)",
        title="Auditores cobram os requisitos de contingência pendentes",
        character_id="architect",
        character_speech=(
            "Não consigo fechar o protocolo de failover sem os 15% de requisitos que "
            "ficaram abertos na Fase 1! Os auditores avisaram que não assinam o Gate 2 "
            "sem essa definição completa."
        ),
        scenario_context=(
            "A pressa na Fase 1 cobrou o preço: você precisa resolver a pendência antes "
            "de avançar para a Implementação."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Parar, completar a especificação com a PO e fechar arquitetura formal",
                description="Absorver o atraso agora para restabelecer rastreabilidade total.",
                impact=MetricImpact(
                    performance=+8,
                    satisfaction=+4,
                    budget=-230_000,
                    deadline_weeks=-5,
                    morale=-4,
                    progress=+22,
                ),
                next_node_id="as_wf_03",
                character_reaction=(
                    "Perdemos tempo voltando à Fase 1, mas agora o Gate 2 está limpo e "
                    "os desenvolvedores podem codar com segurança."
                ),
                educational_note=(
                    "Mesmo no Waterfall, corrigir requisitos ainda na fase de Projeto é "
                    "muito mais barato do que na fase de Testes."
                ),
                tags=["compliance", "rework"],
            ),
            DecisionOption(
                id="B",
                label="Adotar premissas internas e empurrar a pendência para a Implementação",
                description="Evitar atraso imediato assumindo risco de auditoria.",
                impact=MetricImpact(
                    performance=-12,
                    satisfaction=-12,
                    budget=-160_000,
                    deadline_weeks=-3,
                    morale=-10,
                    progress=+20,
                ),
                next_node_id="as_wf_03",
                character_reaction=(
                    "Seguimos adiante, mas o auditor anotou não-conformidade aberta. "
                    "Isso vai pesar forte na certificação."
                ),
                educational_note=(
                    "Ignorar gates formais em projetos regulados cria passivos que "
                    "bloqueiam a homologação final."
                ),
                tags=["rework", "compliance"],
            ),
        ],
    ),
    "as_wf_03": DecisionNode(
        id="as_wf_03",
        stage_name="Fase 3: Implementação (Como)",
        title="Codificação do Núcleo de Radar & Pedido de Alteração Formal (CCB)",
        character_id="backend_dev",
        character_speech=(
            "A codificação do processador de radar e do console dos controladores está "
            "dentro da especificação. Chegou uma solicitação da equipe de operações para "
            "adicionar um novo filtro visual de clima no radar. Como tratamos isso?"
        ),
        scenario_context=(
            "Mesmo em projetos estáveis, pedidos de melhoria podem surgir. A governança "
            "formal de mudanças (CCB) decide se e como incorporar."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Submeter ao Comitê de Controle de Mudanças (CCB) para a Fase 2 pós-certificação",
                description="Proteger a baseline certificável atual e planejar o filtro como evolução formal.",
                impact=MetricImpact(
                    performance=+8,
                    satisfaction=+6,
                    budget=-240_000,
                    deadline_weeks=-5,
                    morale=+5,
                    progress=+22,
                ),
                next_node_id="as_wf_04",
                character_reaction=(
                    "Excelente governança! O comitê aprovou deixar o filtro para o pacote "
                    "de manutenção 1.1 e nossa implementação fechou 100% aderente à spec."
                ),
                educational_note=(
                    "O controle formal de mudanças (CCB) no Waterfall protege sistemas "
                    "críticos contra scope creep sem perder transparência com o cliente."
                ),
                tags=["compliance", "negotiation"],
            ),
            DecisionOption(
                id="B",
                label="Implementar o filtro informalmente sem atualizar os documentos de spec",
                description="Fazer um agrado rápido aos operadores fora do processo formal.",
                impact=MetricImpact(
                    performance=-10,
                    satisfaction=-8,
                    budget=-260_000,
                    deadline_weeks=-5,
                    morale=-8,
                    progress=+20,
                ),
                next_node_id="as_wf_04",
                character_reaction=(
                    "O código ficou divergente da matriz de rastreabilidade! Os auditores "
                    "vão exigir explicação na fase de testes."
                ),
                educational_note=(
                    "Em software certificado, código fora da especificação formal é tratado "
                    "como não-conformidade grave, não como 'bônus'."
                ),
                tags=["rework", "compliance"],
            ),
        ],
    ),
    "as_wf_04": DecisionNode(
        id="as_wf_04",
        stage_name="Fase 4: Teste & Certificação (Como)",
        title="Bateria de Testes Formais, Cobertura MC/DC e Simulador de Torre",
        character_id="qa_engineer",
        character_speech=(
            "Iniciamos a bateria formal de testes com simulador de 500 aeronaves "
            "simultâneas. Falta atingir 100% de cobertura estrutural MC/DC exigida pela "
            "norma DO-178C em dois módulos de alerta de colisão."
        ),
        scenario_context=(
            "A certificação aeronáutica exige evidências formais completas de teste "
            "antes de autorizar a implantação em torre."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Completar 100% de cobertura MC/DC e gerar dossiê completo de auditoria",
                description="Garantir certificação sem ressalvas junto à autoridade aeronáutica.",
                impact=MetricImpact(
                    performance=+12,
                    satisfaction=+10,
                    budget=-220_000,
                    deadline_weeks=-5,
                    morale=+4,
                    progress=+20,
                ),
                next_node_id="as_wf_05",
                character_reaction=(
                    "Certificação aprovada com 0 não-conformidades críticas! O dossiê "
                    "de rastreabilidade está 100% fechado."
                ),
                educational_note=(
                    "No Waterfall bem executado em projetos críticos, a fase de testes "
                    "valida sistematicamente cada requisito especificado na Fase 1."
                ),
                tags=["quality", "compliance"],
            ),
            DecisionOption(
                id="B",
                label="Tentar negociar dispensa parcial dos testes para antecipar entrega",
                description="Pedir exceção aos auditores alegando baixo risco nos 2 módulos.",
                impact=MetricImpact(
                    performance=-14,
                    satisfaction=-16,
                    budget=-180_000,
                    deadline_weeks=-4,
                    morale=-10,
                    progress=+18,
                ),
                next_node_id="as_wf_05",
                character_reaction=(
                    "Os auditores recusaram a dispensa e emitiram advertência formal. "
                    "Tivemos que correr sob pressão para fechar o mínimo aceitável."
                ),
                educational_note=(
                    "Em domínios regulados de alta criticidade, atalhos em testes nunca "
                    "compensam o risco operacional e legal."
                ),
                tags=["rework", "overtime"],
            ),
        ],
    ),
    "as_wf_05": DecisionNode(
        id="as_wf_05",
        stage_name="Fase 5 & 6: Implantação e Manutenção (Software em produção)",
        title="Entrada em Operação na Torre de Controle",
        character_id="devops",
        character_speech=(
            "Recebemos sinal verde da certificação! Podemos rodar o AeroShield ATC em "
            "modo sombra (paralelo ao sistema legado) antes da virada definitiva ou "
            "fazer a substituição direta na madrugada."
        ),
        scenario_context=(
            "Etapa final: transição segura para software em produção e handover de manutenção."
        ),
        is_final_stage=True,
        options=[
            DecisionOption(
                id="A",
                label="Operação em paralelo (Shadow Mode) + treinamento + plano de manutenção",
                description="Validar em tempo real sem risco operacional antes da virada total.",
                impact=MetricImpact(
                    performance=+10,
                    satisfaction=+12,
                    budget=-180_000,
                    deadline_weeks=-3,
                    morale=+6,
                    progress=+25,
                ),
                next_node_id=None,
                character_reaction=(
                    "Transição impecável! Zero segundos de indisponibilidade, operadores "
                    "treinados e contrato de manutenção certificado assinado."
                ),
                educational_note=(
                    "Implantação controlada com transição formal de manutenção coroa o "
                    "ciclo Waterfall em sistemas de missão crítica."
                ),
                tags=["quality", "compliance"],
            ),
            DecisionOption(
                id="B",
                label="Substituição direta na madrugada para economizar custo operacional",
                description="Desligar o legado e ativar o novo sistema de uma vez.",
                impact=MetricImpact(
                    performance=-10,
                    satisfaction=-8,
                    budget=-90_000,
                    deadline_weeks=-2,
                    morale=-10,
                    progress=+25,
                ),
                next_node_id=None,
                character_reaction=(
                    "Entrou no ar, mas um ajuste de calibração de radar gerou tensão "
                    "enorme na torre durante os primeiros voos da manhã."
                ),
                educational_note=(
                    "Mesmo após um bom projeto, viradas abruptas sem redundância "
                    "comprometem a segurança em ambientes críticos."
                ),
                tags=["big_bang"],
            ),
        ],
    ),

    # =========================================================================
    # ÁRVORE SCRUM — AEROSHIELD ATC (Metodologia inadequada — atrito regulatório)
    # =========================================================================
    "as_scrum_01": DecisionNode(
        id="as_scrum_01",
        stage_name="Sprint 0 — Backlog Ágil vs. Contrato Regulado",
        title="Auditores questionam a ausência de especificação congelada",
        character_id="product_owner",
        character_speech=(
            "Propusemos trabalhar em Sprints curtas de 2 semanas com backlog evolutivo, "
            "mas o auditor da aviação civil travou a reunião: ele exige o documento "
            "completo de requisitos e rastreabilidade ANTES de aprovar o início do código!"
        ),
        scenario_context=(
            "Logo no início, o Scrum colide com a exigência legal de documentação "
            "completa e gates sequenciais."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Adaptar o Scrum (híbrido): gastar Sprints iniciais documentando a spec",
                description="Reduzir o choque regulatório criando documentação formal antes de codar.",
                impact=MetricImpact(
                    performance=+4,
                    satisfaction=-4,
                    budget=-200_000,
                    deadline_weeks=-5,
                    morale=-6,
                    progress=+18,
                ),
                next_node_id="as_scrum_02_hybrid",
                character_reaction=(
                    "O auditor aceitou continuar, mas na prática estamos gastando tempo "
                    "com cerimônias ágeis E burocracia formal ao mesmo tempo."
                ),
                educational_note=(
                    "Em projetos altamente regulados, tentar aplicar Scrum puro geralmente "
                    "exige adaptação pesada para documentação, perdendo parte da agilidade."
                ),
                tags=["compliance", "documentation"],
            ),
            DecisionOption(
                id="B",
                label="Insistir no Scrum puro e começar a codificar um MVP já na Sprint 1",
                description="Mostrar software funcionando rápido esperando convencer os auditores.",
                impact=MetricImpact(
                    performance=-8,
                    satisfaction=-14,
                    budget=-180_000,
                    deadline_weeks=-4,
                    morale=-4,
                    progress=+16,
                ),
                next_node_id="as_scrum_02_audit",
                character_reaction=(
                    "Os auditores emitiram alerta formal! Eles disseram que código escrito "
                    "sem baseline aprovada pode ter que ser descartado."
                ),
                educational_note=(
                    "Valorizar 'software funcionando mais que documentação abrangente' "
                    "sem respeitar normas legais gera bloqueios graves em sistemas críticos."
                ),
                tags=["audit", "compliance"],
            ),
        ],
    ),
    "as_scrum_02_audit": DecisionNode(
        id="as_scrum_02_audit",
        stage_name="Sprint 1 — Bloqueio de Auditoria",
        title="Auditoria rejeita código incremental sem arquitetura congelada",
        character_id="architect",
        character_speech=(
            "A auditoria revisou o incremento da Sprint 1 e bloqueou a homologação: "
            "como mudamos a interface de radar entre a Sprint 0 e a 1 sem revisão formal "
            "de segurança, eles exigem refazer os artefatos de arquitetura!"
        ),
        scenario_context=(
            "A iteratividade do Scrum virou retrabalho documental pesado sob a norma DO-178C."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Congelar a arquitetura agora e reescrever toda a documentação retroativa",
                description="Pagar o custo do retrabalho para destravar a auditoria.",
                impact=MetricImpact(
                    performance=+6,
                    satisfaction=-6,
                    budget=-240_000,
                    deadline_weeks=-5,
                    morale=-12,
                    progress=+20,
                ),
                next_node_id="as_scrum_03",
                character_reaction=(
                    "Destravamos o bloqueio, mas o time passou 3 semanas escrevendo documentos "
                    "retroativos em vez de programar."
                ),
                educational_note=(
                    "Documentação retroativa após codificação iterativa custa mais caro "
                    "do que o fluxo sequencial planejado do Waterfall."
                ),
                tags=["documentation", "audit", "rework"],
            ),
            DecisionOption(
                id="B",
                label="Continuar iterando em paralelo e tentar conciliar na reta final",
                description="Manter o ritmo das Sprints deixando a papelada para depois.",
                impact=MetricImpact(
                    performance=-12,
                    satisfaction=-16,
                    budget=-210_000,
                    deadline_weeks=-4,
                    morale=-10,
                    progress=+18,
                ),
                next_node_id="as_scrum_03",
                character_reaction=(
                    "O passivo de auditoria virou uma bola de neve. A equipe sabe que "
                    "vai enfrentar uma muralha na certificação."
                ),
                educational_note=(
                    "Adiar conformidade regulatória em sistemas críticos acumula risco "
                    "incontrolável de reprovação."
                ),
                tags=["audit", "compliance", "rework"],
            ),
        ],
    ),
    "as_scrum_02_hybrid": DecisionNode(
        id="as_scrum_02_hybrid",
        stage_name="Sprint 1 — Sobrecarga de Cerimônias e Documentação",
        title="Custo duplo: Sprints curtas + Dossiês Formais",
        character_id="architect",
        character_speech=(
            "A cada pequena refatoração de arquitetura na Sprint, precisamos atualizar "
            "4 documentos de conformidade e colher assinatura do comitê de segurança. "
            "O time está perdendo 35% do tempo só em burocracia de ciclo curto."
        ),
        scenario_context=(
            "Você sente na prática o custo de manter cadência ágil dentro de um processo "
            "fortemente sequencial e auditado."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Alongar os ciclos e congelar a arquitetura central até a certificação",
                description="Reduzir churn documental adotando disciplina próxima ao Waterfall.",
                impact=MetricImpact(
                    performance=+8,
                    satisfaction=+4,
                    budget=-190_000,
                    deadline_weeks=-4,
                    morale=+2,
                    progress=+22,
                ),
                next_node_id="as_scrum_03",
                character_reaction=(
                    "Melhorou bastante! Menos reabertura de documento e mais foco no "
                    "núcleo de telemetria."
                ),
                educational_note=(
                    "Adaptar o processo quando o contexto exige estabilidade evita "
                    "desperdício com cerimônias desnecessárias."
                ),
                tags=["compliance", "quality"],
            ),
            DecisionOption(
                id="B",
                label="Manter Sprints curtas de 2 semanas atualizando dossiês toda quinzena",
                description="Seguir o guia Scrum à risca apesar do custo documental.",
                impact=MetricImpact(
                    performance=-4,
                    satisfaction=-6,
                    budget=-230_000,
                    deadline_weeks=-5,
                    morale=-14,
                    progress=+20,
                ),
                next_node_id="as_scrum_03",
                character_reaction=(
                    "Os desenvolvedores estão frustrados: passam quase metade da Sprint "
                    "preenchendo evidências repetidas."
                ),
                educational_note=(
                    "Aplicar qualquer metodologia de forma dogmática, ignorando as "
                    "restrições do domínio, destrói produtividade e moral."
                ),
                tags=["documentation", "compliance"],
            ),
        ],
    ),
    "as_scrum_03": DecisionNode(
        id="as_scrum_03",
        stage_name="Sprint 2 — Integração de Radar & Console",
        title="Incrementos parciais não podem ir para produção",
        character_id="frontend_dev",
        character_speech=(
            "Terminei o console visual dos controladores e o Lucas terminou o módulo de "
            "radar, mas na Sprint Review descobrimos um detalhe: os operadores não podem "
            "testar em ambiente real nem receber releases parciais até o pacote 100% certificado!"
        ),
        scenario_context=(
            "Sem releases reais intermediárias, o principal benefício de feedback em "
            "produção do Scrum fica bloqueado pelo ambiente aeronáutico."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Investir em simulador de torre de alta fidelidade para as Reviews",
                description="Criar ambiente simulado realista para validar com controladores.",
                impact=MetricImpact(
                    performance=+8,
                    satisfaction=+6,
                    budget=-220_000,
                    deadline_weeks=-4,
                    morale=+4,
                    progress=+22,
                ),
                next_node_id="as_scrum_04",
                character_reaction=(
                    "O simulador custou caro, mas finalmente os controladores conseguiram "
                    "dar feedback útil sobre a leitura dos alertas de colisão."
                ),
                educational_note=(
                    "Quando não é possível fazer deploy contínuo, simulações ajudam a "
                    "validar UX, mas elevam o custo total do projeto."
                ),
                tags=["quality"],
            ),
            DecisionOption(
                id="B",
                label="Fazer Reviews apenas com slides e telas estáticas para poupar verba",
                description="Evitar gasto extra mantendo o fluxo das Sprints.",
                impact=MetricImpact(
                    performance=-6,
                    satisfaction=-10,
                    budget=-140_000,
                    deadline_weeks=-3,
                    morale=-6,
                    progress=+20,
                ),
                next_node_id="as_scrum_04",
                character_reaction=(
                    "As Reviews viraram reuniões burocráticas sem validação técnica real."
                ),
                educational_note=(
                    "Sem incremento testável em condições reais, o Scrum perde sua "
                    "vantagem de aprendizado empírico."
                ),
                tags=["late_feedback"],
            ),
        ],
    ),
    "as_scrum_04": DecisionNode(
        id="as_scrum_04",
        stage_name="Sprint 3 — Homologação & Certificação DO-178C",
        title="Auditoria exige congelamento total e rastreabilidade 100%",
        character_id="qa_engineer",
        character_speech=(
            "Chegamos à certificação! Como vários módulos evoluíram ao longo de Sprints "
            "diferentes, há lacunas na matriz ligando cada caso de teste ao requisito "
            "original. Sem fechar 100%, a torre não autoriza o uso!"
        ),
        scenario_context=(
            "A reta final cobra a fatura da documentação e cobertura formal."
        ),
        options=[
            DecisionOption(
                id="A",
                label="Criar Sprint de Hardening e Força-Tarefa de Certificação",
                description="Parar desenvolvimento e reconciliar todos os testes e evidências.",
                impact=MetricImpact(
                    performance=+10,
                    satisfaction=+4,
                    budget=-220_000,
                    deadline_weeks=-5,
                    morale=-8,
                    progress=+20,
                ),
                next_node_id="as_scrum_05",
                character_reaction=(
                    "Deu muito trabalho reconciliar o histórico das Sprints, mas "
                    "fechamos o dossiê e conseguimos a aprovação para implantar!"
                ),
                educational_note=(
                    "Projetos críticos conduzidos em Scrum frequentemente acabam criando "
                    "uma fase final pesada de certificação parecida com o fim do Waterfall."
                ),
                tags=["certification", "audit", "overtime"],
            ),
            DecisionOption(
                id="B",
                label="Submeter dossiê parcial com plano de correção pós-entrega",
                description="Tentar cumprir o prazo apostando em aprovação condicional.",
                impact=MetricImpact(
                    performance=-14,
                    satisfaction=-18,
                    budget=-190_000,
                    deadline_weeks=-4,
                    morale=-12,
                    progress=+18,
                ),
                next_node_id="as_scrum_05",
                character_reaction=(
                    "A autoridade aeronáutica impôs restrições severas de operação e "
                    "exigiu auditoria extraordinária caríssima."
                ),
                educational_note=(
                    "Em sistemas críticos, certificação parcial raramente é aceita e "
                    "derruba drasticamente a confiança do contratante."
                ),
                tags=["certification", "audit"],
            ),
        ],
    ),
    "as_scrum_05": DecisionNode(
        id="as_scrum_05",
        stage_name="Release Final — Entrada em Operação na Torre",
        title="Transição do Projeto Ágil para Operação Certificada",
        character_id="devops",
        character_speech=(
            "Estamos prontos para colocar o AeroShield ATC na torre. Precisamos definir "
            "como faremos a virada e a entrega da documentação operacional."
        ),
        scenario_context=(
            "Decisão final do projeto em ambiente de missão crítica."
        ),
        is_final_stage=True,
        options=[
            DecisionOption(
                id="A",
                label="Implantação em Shadow Mode + pacote completo de operação e manutenção",
                description="Priorizar segurança máxima na entrada em produção.",
                impact=MetricImpact(
                    performance=+8,
                    satisfaction=+8,
                    budget=-170_000,
                    deadline_weeks=-3,
                    morale=+4,
                    progress=+25,
                ),
                next_node_id=None,
                character_reaction=(
                    "Sistema em operação com segurança! Foi mais caro e trabalhoso do que "
                    "seria no Waterfall, mas conseguimos entregar sem incidentes."
                ),
                educational_note=(
                    "É possível entregar um projeto regulado usando práticas ágeis, mas "
                    "com sobrecarga de governança bem maior que no Waterfall."
                ),
                tags=["compliance", "quality"],
            ),
            DecisionOption(
                id="B",
                label="Virada direta rápida para tentar estancar o estouro de orçamento",
                description="Cortar período de operação paralela.",
                impact=MetricImpact(
                    performance=-12,
                    satisfaction=-12,
                    budget=-90_000,
                    deadline_weeks=-2,
                    morale=-10,
                    progress=+25,
                ),
                next_node_id=None,
                character_reaction=(
                    "Entramos no ar sob forte tensão. Tivemos alertas falsos nas primeiras "
                    "horas que desgastaram ainda mais a relação com a autoridade."
                ),
                educational_note=(
                    "Cortar segurança na implantação para compensar atrasos anteriores "
                    "amplifica o risco em software crítico."
                ),
                tags=["big_bang"],
            ),
        ],
    ),
}
