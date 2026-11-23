/* Controlador da Interface Pixel 2D — Scrum vs. Waterfall
 *
 * Fluxo de telas por turno (sem poluição visual):
 *   1. "map_before" -> Mostra APENAS o mapa da metodologia (Cascata ou Scrum) antes da decisão
 *   2. "decision"   -> Oculta o mapa e mostra APENAS o personagem 2D pixelado + opções A/B/C
 *   3. "map_after"  -> Mostra o mapa atualizado (descida ou retorno em erro) + feedback/impacto
 */

const appState = {
  cases: [],
  config: null,
  selectedCaseId: null,
  selectedMethod: null,
  game: null,
  phase: "map_before", // "map_before" | "decision" | "map_after"
};

const CHARACTER_APPEARANCE = {
  backend_dev:   { shirt: "#2563eb", trim: "#60a5fa", hair: "#1e293b", skin: "#f1c27d", glasses: true },
  frontend_dev:  { shirt: "#db2777", trim: "#f472b6", hair: "#451a03", skin: "#ffdbac", glasses: false },
  architect:     { shirt: "#4f46e5", trim: "#a5b4fc", hair: "#475569", skin: "#e0ac69", glasses: true },
  qa_engineer:   { shirt: "#0d9488", trim: "#5eead4", hair: "#7c2d12", skin: "#f1c27d", glasses: false },
  devops:        { shirt: "#ea580c", trim: "#fdba74", hair: "#0f172a", skin: "#c68642", glasses: false },
  ux_designer:   { shirt: "#9333ea", trim: "#d8b4fe", hair: "#713f12", skin: "#ffdbac", glasses: true },
  product_owner: { shirt: "#059669", trim: "#6ee7b7", hair: "#292524", skin: "#e0ac69", glasses: false },
};

const WATERFALL_STAGE_LABELS = [
  "Requisitos",
  "Projeto",
  "Implementação",
  "Teste",
  "Implantação",
  "Manutenção",
];

function fmtMoney(val) {
  const sign = val < 0 ? "-" : "";
  return `${sign}R$ ${Math.abs(val).toLocaleString("pt-BR")}`;
}

function fmtDelta(val, suffix = "") {
  return val > 0 ? `+${val}${suffix}` : `${val}${suffix}`;
}

async function apiGet(path) {
  const res = await fetch(path);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

function switchScreen(id) {
  document.querySelectorAll(".screen").forEach((el) => el.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

/* ==================== SPRITE PIXEL ART 16x18 DOS PERSONAGENS ==================== */
function renderPixelCharacterSVG(charId, mood = "neutral", mini = false) {
  const st = CHARACTER_APPEARANCE[charId] || CHARACTER_APPEARANCE.backend_dev;

  let mouth = `<rect x="7" y="9" width="2" height="1" fill="#0f172a"/>`;
  let moodIcon = "";

  if (mood === "happy") {
    mouth = `
      <rect x="6" y="8" width="1" height="1" fill="#0f172a"/>
      <rect x="7" y="9" width="2" height="1" fill="#0f172a"/>
      <rect x="9" y="8" width="1" height="1" fill="#0f172a"/>
    `;
    moodIcon = `
      <rect x="13" y="1" width="3" height="3" fill="#22c55e"/>
      <rect x="14" y="2" width="1" height="1" fill="#fff"/>
    `;
  } else if (mood === "worried") {
    mouth = `
      <rect x="6" y="9" width="1" height="1" fill="#0f172a"/>
      <rect x="7" y="8" width="2" height="1" fill="#0f172a"/>
      <rect x="9" y="9" width="1" height="1" fill="#0f172a"/>
    `;
    moodIcon = `
      <rect x="13" y="1" width="3" height="3" fill="#ef4444"/>
      <rect x="14" y="1" width="1" height="2" fill="#fff"/>
    `;
  }

  const glasses = st.glasses
    ? `
      <rect x="5" y="6" width="3" height="2" fill="none" stroke="#0f172a" stroke-width="0.6"/>
      <rect x="8" y="6" width="3" height="2" fill="none" stroke="#0f172a" stroke-width="0.6"/>
    `
    : "";

  const reactionCls =
    !mini && mood === "happy"
      ? "react-happy"
      : !mini && mood === "worried"
      ? "react-worried"
      : "";

  return `
    <svg class="char-sprite ${mini ? "mini" : ""} ${reactionCls}" viewBox="0 0 16 18" shape-rendering="crispEdges" aria-hidden="true">
      <!-- Sombra pixelada -->
      <rect x="3" y="17" width="10" height="1" fill="rgba(0,0,0,0.4)"/>
      <!-- Cabelo topo -->
      <rect x="5" y="2" width="6" height="2" fill="${st.hair}"/>
      <rect x="4" y="3" width="8" height="2" fill="${st.hair}"/>
      <!-- Cabeça / rosto -->
      <rect x="4" y="5" width="8" height="5" fill="${st.skin}"/>
      <rect x="5" y="10" width="6" height="1" fill="${st.skin}"/>
      <!-- Olhos -->
      <rect x="6" y="6" width="1" height="2" fill="#0f172a"/>
      <rect x="9" y="6" width="1" height="2" fill="#0f172a"/>
      ${glasses}
      ${mouth}
      <!-- Pescoço -->
      <rect x="7" y="11" width="2" height="1" fill="${st.skin}"/>
      <!-- Tronco / Camisa -->
      <rect x="3" y="12" width="10" height="5" fill="${st.shirt}"/>
      <rect x="4" y="12" width="8" height="1" fill="${st.trim}"/>
      <!-- Braços -->
      <rect x="2" y="13" width="1" height="4" fill="${st.shirt}"/>
      <rect x="13" y="13" width="1" height="4" fill="${st.shirt}"/>
      <!-- Crachá pixelado -->
      <rect x="9" y="13" width="2" height="3" fill="#f8fafc"/>
      <rect x="9" y="13" width="2" height="1" fill="${st.trim}"/>
      ${moodIcon}
    </svg>
  `;
}

/* ==================== VISUALIZADOR PIXEL 2D: WATERFALL (CASCATA) ==================== */
function renderWaterfallViz(currentStageIdx, rollbackFromIdx = null, rollbackToIdx = null) {
  const steps = [
    { x: 122, y: 18, label: "REQUISITOS" },
    { x: 260, y: 56, label: "PROJETO" },
    { x: 398, y: 94, label: "IMPLEMENTAÇÃO" },
    { x: 536, y: 132, label: "TESTE" },
    { x: 674, y: 170, label: "IMPLANTAÇÃO" },
    { x: 812, y: 208, label: "MANUTENÇÃO" },
  ];
  const w = 136;
  const h = 30;

  const isRollback =
    rollbackFromIdx !== null &&
    rollbackToIdx !== null &&
    rollbackToIdx < rollbackFromIdx;

  const activeIdx = isRollback ? rollbackToIdx : Math.min(currentStageIdx, steps.length - 1);

  let downArrows = "";
  for (let i = 0; i < steps.length - 1; i++) {
    const a = steps[i];
    const b = steps[i + 1];
    const done = i < currentStageIdx;
    const stroke = done ? "#38bdf8" : "#4e6291";
    downArrows += `
      <path d="M ${a.x + w} ${a.y + 15} H ${b.x + w / 2} V ${b.y - 4}"
            fill="none" stroke="${stroke}" stroke-width="3" marker-end="url(#px-arrow)" />
    `;
  }

  let dottedFeedback = `<line x1="190" y1="246" x2="812" y2="246" stroke="#3b4b72" stroke-width="2" stroke-dasharray="6 4"/>`;
  for (let i = 0; i < steps.length - 1; i++) {
    const s = steps[i];
    dottedFeedback += `
      <line x1="${s.x + w / 2}" y1="246" x2="${s.x + w / 2}" y2="${s.y + h + 4}"
            stroke="#3b4b72" stroke-width="2" stroke-dasharray="6 4" />
    `;
  }

  let rollbackOverlay = "";
  if (isRollback) {
    const from = steps[Math.min(rollbackFromIdx, steps.length - 1)];
    const to = steps[Math.min(rollbackToIdx, steps.length - 1)];
    const xFrom = from.x + w / 2;
    const yFrom = from.y + h;
    const xTo = to.x + w / 2;
    const yTo = to.y + h + 5;
    rollbackOverlay = `
      <path class="wf-rollback-path"
            d="M ${xFrom} ${yFrom} V 252 H ${xTo} V ${yTo}"
            fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#px-arrow-red)" />
      <rect x="${(xFrom + xTo) / 2 - 140}" y="238" width="280" height="22" fill="#5c1212" stroke="#ef4444" stroke-width="2"/>
      <text x="${(xFrom + xTo) / 2}" y="253" text-anchor="middle" fill="#fecaca" font-family="Courier New, monospace" font-size="12" font-weight="700">
        ! ERRO: VOLTA P/ ${steps[rollbackToIdx].label} !
      </text>
    `;
  }

  let boxes = "";
  steps.forEach((s, idx) => {
    let fill = "#1e3a8a";
    let stroke = "#3b82f6";
    if (idx < currentStageIdx) {
      fill = "#0369a1";
      stroke = "#38bdf8";
    }
    if (idx === activeIdx) {
      fill = isRollback ? "#991b1b" : "#2563eb";
      stroke = isRollback ? "#f87171" : "#facc15";
    }
    boxes += `
      <g>
        <rect x="${s.x + 4}" y="${s.y + 4}" width="${w}" height="${h}" fill="#090d16"/>
        <rect x="${s.x}" y="${s.y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" stroke-width="${idx === activeIdx ? 4 : 2}"/>
        <text x="${s.x + w / 2}" y="${s.y + 19}" text-anchor="middle" fill="#f8fafc" font-family="Courier New, monospace" font-size="12" font-weight="700">${s.label}</text>
      </g>
    `;
  });

  const tokenTarget = steps[activeIdx];
  const tokenX = tokenTarget.x + 12;
  const tokenY = tokenTarget.y - 12;

  return `
    <svg class="viz-svg" viewBox="0 0 980 266" shape-rendering="crispEdges">
      <defs>
        <marker id="px-arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
        </marker>
        <marker id="px-arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="7" markerHeight="7" orient="auto">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
        </marker>
      </defs>

      <!-- Faixas horizontais da cascata (O quê / Como / Software em produção) -->
      <line x1="10" y1="90" x2="970" y2="90" stroke="#4e6291" stroke-width="2" stroke-dasharray="8 6"/>
      <line x1="10" y1="166" x2="970" y2="166" stroke="#4e6291" stroke-width="2" stroke-dasharray="8 6"/>

      <text x="14" y="80" fill="#a6b7d6" font-family="Courier New, monospace" font-size="13" font-weight="700">O QUÊ</text>
      <text x="14" y="156" fill="#a6b7d6" font-family="Courier New, monospace" font-size="13" font-weight="700">COMO</text>
      <text x="14" y="220" fill="#a6b7d6" font-family="Courier New, monospace" font-size="11" font-weight="700">SOFTWARE EM</text>
      <text x="14" y="234" fill="#a6b7d6" font-family="Courier New, monospace" font-size="11" font-weight="700">PRODUÇÃO</text>

      ${dottedFeedback}
      ${downArrows}
      ${boxes}
      ${rollbackOverlay}

      <!-- Marcador Pixel do Projeto -->
      <g class="wf-token" style="transform: translate(${tokenX}px, ${tokenY}px);">
        <rect x="-10" y="-10" width="20" height="20" fill="${isRollback ? "#ef4444" : "#facc15"}" stroke="#090d16" stroke-width="3"/>
        <text x="0" y="5" text-anchor="middle" fill="#090d16" font-family="Courier New, monospace" font-size="13" font-weight="900">${isRollback ? "!" : "★"}</text>
      </g>
    </svg>
  `;
}

/* ==================== VISUALIZADOR PIXEL 2D: SCRUM (CICLO ITERATIVO) ==================== */
function renderScrumViz(currentStageIdx, progress, lastEvent) {
  const sprints = [
    { label: "SPRINT 0", sub: "DISCOVERY" },
    { label: "SPRINT 1", sub: "MVP" },
    { label: "SPRINT 2", sub: "EVOLUÇÃO" },
    { label: "SPRINT 3", sub: "ESCALA" },
    { label: "RELEASE", sub: "PRODUÇÃO" },
  ];

  const activeIdx = Math.min(currentStageIdx, sprints.length - 1);
  const doneCount = Math.min(4, Math.floor(progress / 25));

  let timeline = "";
  sprints.forEach((sp, idx) => {
    const x = 248 + idx * 142;
    const isDone = idx < activeIdx || progress >= 100;
    const isCurrent = idx === activeIdx && progress < 100;
    const fill = isCurrent ? "#16a34a" : isDone ? "#065f46" : "#1e2740";
    const stroke = isCurrent ? "#facc15" : isDone ? "#22c55e" : "#4e6291";

    if (idx < sprints.length - 1) {
      timeline += `<line x1="${x + 116}" y1="68" x2="${x + 142}" y2="68" stroke="${isDone ? "#22c55e" : "#4e6291"}" stroke-width="4" />`;
    }

    timeline += `
      <g>
        <rect x="${x + 4}" y="46" width="116" height="52" fill="#090d16"/>
        <rect x="${x}" y="42" width="116" height="52" fill="${fill}" stroke="${stroke}" stroke-width="${isCurrent ? 4 : 2}"/>
        <text x="${x + 58}" y="64" text-anchor="middle" fill="#f8fafc" font-family="Courier New, monospace" font-size="12" font-weight="700">${sp.label}</text>
        <text x="${x + 58}" y="82" text-anchor="middle" fill="#cbd5e1" font-family="Courier New, monospace" font-size="10">${sp.sub}</text>
      </g>
    `;
  });

  let kanbanCards = "";
  for (let i = 0; i < 4; i++) {
    const colX = i < doneCount ? 780 : i === doneCount ? 516 : 272;
    const offsetY = 132 + (i % 2) * 20;
    const offsetX = colX + Math.floor(i / 2) * 86;
    const cardColor = i < doneCount ? "#22c55e" : i === doneCount ? "#facc15" : "#38bdf8";
    kanbanCards += `<rect x="${offsetX}" y="${offsetY}" width="74" height="14" fill="${cardColor}" stroke="#090d16" stroke-width="2"/>`;
  }

  const cycleAlert =
    lastEvent && lastEvent.tags && lastEvent.tags.includes("scope_change")
      ? "★ BACKLOG REPRIORIZADO NA SPRINT!"
      : "CICLO ÁGIL: PLANNING → BUILD → REVIEW → RETRO";

  return `
    <svg class="viz-svg" viewBox="0 0 980 190" shape-rendering="crispEdges">
      <g>
        <rect x="52" y="34" width="120" height="118" fill="#131b2e" stroke="#22c55e" stroke-width="3"/>
        <g class="scrum-spin">
          <rect x="96" y="48" width="32" height="8" fill="#22c55e"/>
          <rect x="144" y="76" width="8" height="32" fill="#22c55e"/>
          <rect x="96" y="128" width="32" height="8" fill="#22c55e"/>
          <rect x="72" y="76" width="8" height="32" fill="#facc15"/>
        </g>
        <text x="112" y="90" text-anchor="middle" fill="#4ade80" font-family="Courier New, monospace" font-size="12" font-weight="700">${sprints[activeIdx].label}</text>
        <text x="112" y="106" text-anchor="middle" fill="#cbd5e1" font-family="Courier New, monospace" font-size="10">LOOP ÁGIL</text>
      </g>

      <text x="248" y="26" fill="#facc15" font-family="Courier New, monospace" font-size="12" font-weight="700">${cycleAlert}</text>
      ${timeline}

      <rect x="248" y="110" width="224" height="68" fill="#131b2e" stroke="#4e6291" stroke-width="3"/>
      <text x="262" y="125" fill="#a6b7d6" font-family="Courier New, monospace" font-size="10" font-weight="700">BACKLOG</text>

      <rect x="492" y="110" width="224" height="68" fill="#131b2e" stroke="#4e6291" stroke-width="3"/>
      <text x="506" y="125" fill="#facc15" font-family="Courier New, monospace" font-size="10" font-weight="700">EM SPRINT</text>

      <rect x="736" y="110" width="224" height="68" fill="#131b2e" stroke="#4e6291" stroke-width="3"/>
      <text x="750" y="125" fill="#4ade80" font-family="Courier New, monospace" font-size="10" font-weight="700">ENTREGUE</text>

      ${kanbanCards}
    </svg>
  `;
}

/* ==================== TELA INICIAL ==================== */
async function initStartScreen() {
  const data = await apiGet("/api/cases");
  appState.cases = data.cases;
  appState.config = data.config;

  const container = document.getElementById("cases-container");
  container.innerHTML = "";

  data.cases.forEach((c) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "case-card";
    btn.dataset.caseId = c.id;
    btn.innerHTML = `
      <h3>${c.name}</h3>
      <div class="case-sub">${c.subtitle}</div>
      <div class="case-meta">
        <span>ORÇ: ${fmtMoney(c.initial_metrics.budget)}</span>
        <span>PRAZO: ${c.initial_metrics.deadline_weeks} SEM.</span>
      </div>
    `;
    btn.addEventListener("click", () => {
      appState.selectedCaseId = c.id;
      document.querySelectorAll(".case-card").forEach((el) => el.classList.remove("selected"));
      btn.classList.add("selected");

      document.getElementById("brief-text").textContent = c.description;
      document.getElementById("selected-case-brief").classList.remove("hidden");
      updateStartButton();
    });
    container.appendChild(btn);
  });

  document.querySelectorAll(".method-card").forEach((btn) => {
    btn.addEventListener("click", () => {
      appState.selectedMethod = btn.dataset.method;
      document.querySelectorAll(".method-card").forEach((el) => el.classList.remove("selected"));
      btn.classList.add("selected");
      updateStartButton();
    });
  });

  document.getElementById("btn-start-game").addEventListener("click", startGame);
  document.getElementById("btn-back-home").addEventListener("click", () => switchScreen("screen-start"));
  document.getElementById("btn-play-again").addEventListener("click", () => switchScreen("screen-start"));
  document.getElementById("btn-enter-decision").addEventListener("click", enterDecisionPhase);
  document.getElementById("btn-next-turn").addEventListener("click", advanceAfterFeedback);
  document.getElementById("btn-negotiate-accept").addEventListener("click", () => sendNegotiation(true));
  document.getElementById("btn-negotiate-reject").addEventListener("click", () => sendNegotiation(false));
}

function updateStartButton() {
  document.getElementById("btn-start-game").disabled = !(appState.selectedCaseId && appState.selectedMethod);
}

async function startGame() {
  const state = await apiPost("/api/start", {
    case_id: appState.selectedCaseId,
    methodology: appState.selectedMethod,
  });
  appState.game = state;
  appState.phase = "map_before"; // Começa mostrando o mapa da metodologia ANTES da decisão
  switchScreen("screen-game");
  renderGameScreen();
}

/* ==================== RENDERIZAÇÃO DA TELA DE JOGO ==================== */
function renderHUD(g) {
  const badge = document.getElementById("hud-methodology-badge");
  badge.textContent = g.methodology;
  badge.className = `badge ${g.methodology.toLowerCase()}`;
  document.getElementById("hud-case-name").textContent = g.case.name;
  document.getElementById("hud-stage-label").textContent = g.current_node
    ? `${g.current_node.stage_name} • Turno ${g.turn + (appState.phase === "map_after" ? 0 : 1)}`
    : "Conclusão do Projeto";

  const m = g.metrics;
  document.getElementById("m-progress").textContent = `${m.progress}%`;
  document.getElementById("bar-progress").style.width = `${m.progress}%`;

  document.getElementById("m-performance").textContent = m.performance;
  document.getElementById("bar-performance").style.width = `${m.performance}%`;

  document.getElementById("m-satisfaction").textContent = m.satisfaction;
  document.getElementById("bar-satisfaction").style.width = `${m.satisfaction}%`;

  document.getElementById("m-morale").textContent = m.morale;
  document.getElementById("bar-morale").style.width = `${m.morale}%`;

  const budgetEl = document.getElementById("m-budget");
  budgetEl.textContent = fmtMoney(m.budget);
  budgetEl.classList.toggle("text-danger", m.budget < 0);

  const deadlineEl = document.getElementById("m-deadline");
  deadlineEl.textContent = `${m.deadline_weeks} sem.`;
  deadlineEl.classList.toggle("text-danger", m.deadline_weeks <= 2);
}

function renderMethodologyDiagram(g, evForAfter = null) {
  const vizEl = document.getElementById("methodology-viz");
  const vizTitle = document.getElementById("viz-title");
  const vizStatus = document.getElementById("viz-status-pill");

  if (g.methodology === "WATERFALL") {
    vizTitle.textContent = "VISUALIZAÇÃO WATERFALL — FLUXO EM CASCATA";
    const hasRollback =
      evForAfter &&
      evForAfter.rollback_to_stage !== null &&
      evForAfter.rollback_to_stage !== undefined;

    if (hasRollback) {
      vizStatus.textContent = `RETORNO NA CASCATA → ${WATERFALL_STAGE_LABELS[evForAfter.rollback_to_stage].toUpperCase()}`;
      vizStatus.className = "viz-status-pill rollback";
      vizEl.innerHTML = renderWaterfallViz(
        g.current_stage_index,
        evForAfter.from_stage_index,
        evForAfter.rollback_to_stage
      );
    } else {
      const stageName = WATERFALL_STAGE_LABELS[Math.min(g.current_stage_index, 5)].toUpperCase();
      vizStatus.textContent =
        appState.phase === "map_before"
          ? `PRÓXIMA ETAPA: ${stageName}`
          : `AVANÇOU PARA: ${stageName}`;
      vizStatus.className = "viz-status-pill";
      vizEl.innerHTML = renderWaterfallViz(g.current_stage_index);
    }
  } else {
    vizTitle.textContent = "VISUALIZAÇÃO SCRUM — CICLO ITERATIVO";
    vizStatus.textContent = g.current_node ? g.current_node.stage_name.toUpperCase() : "RELEASE CONCLUÍDA";
    vizStatus.className = "viz-status-pill";
    vizEl.innerHTML = renderScrumViz(g.current_stage_index, g.metrics.progress, evForAfter);
  }
}

function renderGameScreen() {
  const g = appState.game;
  if (!g || !g.active) return;

  renderHUD(g);

  const mapStageEl = document.getElementById("view-methodology-stage");
  const decisionStageEl = document.getElementById("view-decision-stage");
  const beforeFooter = document.getElementById("map-before-footer");
  const afterFooter = document.getElementById("map-after-footer");

  // 1. FASE APÓS A DECISÃO: mostra a Cascata/Scrum + resultado/impacto
  if (appState.phase === "map_after" && g.last_event && !g.last_event.negotiation) {
    mapStageEl.classList.remove("hidden");
    decisionStageEl.classList.add("hidden");
    beforeFooter.classList.add("hidden");
    afterFooter.classList.remove("hidden");

    renderMethodologyDiagram(g, g.last_event);
    renderAfterFeedback(g.last_event);
    return;
  }

  // Checa modal de negociação ou tela final quando sair do feedback
  if (g.status === "AWAITING_DEADLINE_NEGOTIATION") {
    openNegotiationModal(g);
    return;
  }
  if (g.debriefing) {
    renderEndScreen(g);
    return;
  }

  // 2. FASE ANTES DA DECISÃO: mostra APENAS a Cascata/Scrum posicionando o jogador
  if (appState.phase === "map_before" && g.current_node) {
    mapStageEl.classList.remove("hidden");
    decisionStageEl.classList.add("hidden");
    beforeFooter.classList.remove("hidden");
    afterFooter.classList.add("hidden");

    renderMethodologyDiagram(g, null);

    const ch = g.current_node.character;
    document.getElementById("map-next-avatar").innerHTML = renderPixelCharacterSVG(ch.id, "neutral", true);
    document.getElementById("map-before-stage").textContent =
      `TURNO ${g.turn + 1} • ${g.current_node.stage_name.toUpperCase()}`;
    document.getElementById("map-before-summary").textContent =
      `${ch.name} (${ch.role}) está aguardando sua decisão sobre: "${g.current_node.title}".`;
    return;
  }

  // 3. FASE DE DECISÃO LIMPA: oculta o mapa e exibe SOMENTE o personagem 2D + opções
  if (appState.phase === "decision" && g.current_node) {
    mapStageEl.classList.add("hidden");
    decisionStageEl.classList.remove("hidden");
    renderDecisionMode(g.current_node, g.turn + 1);
  }
}

function enterDecisionPhase() {
  appState.phase = "decision";
  renderGameScreen();
}

function renderDecisionMode(node, turnNumber) {
  document.getElementById("board-title").textContent =
    appState.game.methodology === "SCRUM" ? "SCRUM" : "CASCATA";

  const ch = node.character;
  document.getElementById("char-tag").textContent = ch.avatar_tag;
  document.getElementById("char-name").textContent = ch.name;
  document.getElementById("char-role").textContent = `• ${ch.role}`;
  document.getElementById("char-speech").textContent = `"${node.character_speech}"`;
  document.getElementById("character-slot").innerHTML = renderPixelCharacterSVG(ch.id, "neutral", false);

  document.getElementById("event-turn-badge").textContent = `TURNO ${turnNumber} • ${node.stage_name}`;
  document.getElementById("event-title").textContent = node.title;
  document.getElementById("event-context").textContent = node.scenario_context;

  const list = document.getElementById("options-list");
  list.innerHTML = "";
  node.options.forEach((opt) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "option-btn";
    btn.innerHTML = `
      <span class="option-letter">${opt.id}</span>
      <div class="option-body">
        <strong>${opt.label}</strong>
        <span>${opt.description}</span>
      </div>
    `;
    btn.addEventListener("click", () => submitDecision(opt.id));
    list.appendChild(btn);
  });
}

function renderAfterFeedback(ev) {
  document.getElementById("after-avatar").innerHTML = renderPixelCharacterSVG(ev.character.id, ev.mood, true);
  document.getElementById("after-char-tag").textContent = ev.character.avatar_tag;
  document.getElementById("after-char-name").textContent = ev.character.name;
  document.getElementById("after-char-reaction").textContent = `"${ev.character_reaction}"`;

  const moodBadge = document.getElementById("feedback-mood-badge");
  moodBadge.className = `mood-badge ${ev.mood}`;
  moodBadge.textContent =
    ev.mood === "happy" ? "POSITIVO" : ev.mood === "worried" ? "ALERTA" : "TRADE-OFF";

  document.getElementById("feedback-chosen-title").textContent = `[${ev.option_id}] ${ev.option_label}`;

  const rbAlert = document.getElementById("rollback-alert");
  if (ev.rollback_to_stage !== null && ev.rollback_to_stage !== undefined) {
    rbAlert.textContent =
      `! RETORNO NA CASCATA: o erro/retrabalho obrigou o projeto a voltar para "${WATERFALL_STAGE_LABELS[ev.rollback_to_stage]}" antes de prosseguir!`;
    rbAlert.classList.remove("hidden");
  } else {
    rbAlert.classList.add("hidden");
  }

  const imp = ev.applied_impact;
  const chipsData = [
    { label: "PERF", val: imp.performance, text: fmtDelta(imp.performance) },
    { label: "SATISF", val: imp.satisfaction, text: fmtDelta(imp.satisfaction) },
    { label: "ÂNIMO", val: imp.morale, text: fmtDelta(imp.morale) },
    { label: "ORÇ", val: imp.budget, text: fmtMoney(imp.budget) },
    { label: "PRAZO", val: imp.deadline_weeks, text: fmtDelta(imp.deadline_weeks, " sem.") },
    { label: "PROG", val: imp.progress, text: fmtDelta(imp.progress, "%") },
  ];

  document.getElementById("impact-chips").innerHTML = chipsData
    .map((c) => {
      const cls = c.val > 0 ? "pos" : c.val < 0 ? "neg" : "";
      return `<span class="chip ${cls}">${c.label}: ${c.text}</span>`;
    })
    .join("");

  document.getElementById("rules-list").innerHTML = ev.applied_rules.map((r) => `<li>${r}</li>`).join("");
  document.getElementById("lesson-text").textContent = ev.educational_note;

  const nextBtn = document.getElementById("btn-next-turn");
  if (appState.game.status === "AWAITING_DEADLINE_NEGOTIATION") {
    nextBtn.textContent = "► RESOLVER ALERTA DE PRAZO";
  } else if (appState.game.debriefing) {
    nextBtn.textContent = "► VER RELATÓRIO FINAL";
  } else {
    nextBtn.textContent = "► CONTINUAR PARA PRÓXIMA DECISÃO";
  }
}

async function submitDecision(optionId) {
  const state = await apiPost("/api/decide", { option_id: optionId });
  appState.game = state;
  appState.phase = "map_after"; // Após decidir, volta para a tela da Cascata/Scrum com o resultado!
  renderGameScreen();
}

function advanceAfterFeedback() {
  // Ao avançar após ver o mapa atualizado, entra direto na próxima decisão (ou negociação/final)
  appState.phase = "decision";
  renderGameScreen();
}

/* ==================== NEGOCIAÇÃO DE PRAZO ==================== */
function openNegotiationModal(g) {
  document.getElementById("negotiation-text").textContent =
    `O prazo atingiu ${g.metrics.deadline_weeks} semanas, mas sua satisfação está em ${g.metrics.satisfaction}% ` +
    `(mínimo: ${appState.config.min_satisfaction_for_negotiation}%). Você pode negociar ` +
    `+${appState.config.negotiation_extra_weeks} semanas em troca de ${appState.config.negotiation_satisfaction_cost}% ` +
    `de satisfação e custo administrativo adicional.`;
  document.getElementById("modal-negotiation").classList.remove("hidden");
}

async function sendNegotiation(accept) {
  document.getElementById("modal-negotiation").classList.add("hidden");
  const state = await apiPost("/api/negotiate", { accept });
  appState.game = state;
  appState.phase = "map_before";
  renderGameScreen();
}

/* ==================== TELA FINAL ==================== */
function renderEndScreen(g) {
  const d = g.debriefing;
  const delivered = d.status === "DELIVERED";

  const badge = document.getElementById("end-status-badge");
  badge.textContent = delivered ? "★ PROJETO ENTREGUE ★" : "✕ FIM DE JOGO — INTERROMPIDO";
  badge.className = `end-badge ${delivered ? "" : "gameover"}`;

  document.getElementById("end-title").textContent = g.case.name;
  document.getElementById("end-reason").textContent = d.termination_reason;
  document.getElementById("end-grade").textContent = d.grade;
  document.getElementById("end-score").textContent = `${d.score}/100`;
  document.getElementById("end-verdict").textContent = d.verdict;

  const m = g.metrics;
  document.getElementById("end-metrics-grid").innerHTML = `
    <div class="end-metric-box"><span>PERF</span><strong>${m.performance}/100</strong></div>
    <div class="end-metric-box"><span>SATISF</span><strong>${m.satisfaction}/100</strong></div>
    <div class="end-metric-box"><span>ÂNIMO</span><strong>${m.morale}/100</strong></div>
    <div class="end-metric-box"><span>ORÇAMENTO</span><strong>${fmtMoney(m.budget)}</strong></div>
    <div class="end-metric-box"><span>PRAZO</span><strong>${m.deadline_weeks} sem.</strong></div>
  `;

  document.getElementById("end-fit-summary").textContent = d.chose_ideal
    ? `Você escolheu ${d.chosen_methodology} — a metodologia ideal para este case! ${d.ideal_justification}`
    : `Você jogou com ${d.chosen_methodology}, mas o ideal para este case era ${d.ideal_methodology}. ${d.ideal_justification}`;

  document.getElementById("end-scrum-text").textContent = d.scrum_comparison;
  document.getElementById("end-waterfall-text").textContent = d.waterfall_comparison;

  switchScreen("screen-end");
}

window.addEventListener("DOMContentLoaded", initStartScreen);
