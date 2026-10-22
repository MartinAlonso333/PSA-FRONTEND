const DEFAULT_CONFIG = Object.freeze({
  tribeName: "Tribu X",
  mvpName: "MVP integrado",
  frontendUrl: "https://tribu-X.example.com",
  allowedOrigin: "https://tribu-X.example.com",
  backends: [
    {
      name: "Squad X backend",
      purpose: "Dominio A",
      baseUrl: "https://squad-X.example.com",
      healthPath: "/api/health",
      docsPath: "/docs",
      openapiPath: "/v3/api-docs",
    },
    {
      name: "Squad X backend",
      purpose: "Dominio B",
      baseUrl: "https://squad-X.example.com",
      healthPath: "/api/health",
      docsPath: "/docs",
      openapiPath: "/v3/api-docs",
    },
  ],
  checklist: [
    { title: "Vision integrada", detail: "Una sola narrativa de producto, MVP y fuera de alcance." },
    { title: "Modelo de dominio", detail: "Conceptual, compartido y sin vocabulario tecnico." },
    { title: "Frontend desplegado", detail: "Una URL publica que presenta el estado de la tribu." },
    { title: "Backends accesibles", detail: "Ambos servicios responden `GET /api/health` por HTTPS." },
    { title: "CORS verificado", detail: "Los dos backends aceptan el origin del frontend." },
    { title: "Demo lista", detail: "Smoke test y guion de demostracion antes de exponer." },
  ],
  demo: {
    notes: "Antes de mostrar, correr el smoke de produccion y verificar que las dos APIs sigan vivas.",
  },
});

const state = {
  config: DEFAULT_CONFIG,
  backendChecks: [],
  loading: true,
  updatedAt: null,
  error: null,
};

const nodes = {
  tribeTitle: document.getElementById("tribe-title"),
  tribeLead: document.getElementById("tribe-lead"),
  refreshButton: document.getElementById("refresh-button"),
  overallPill: document.getElementById("overall-pill"),
  lastUpdated: document.getElementById("last-updated"),
  summary: document.getElementById("summary"),
  backends: document.getElementById("backends"),
  contract: document.getElementById("contract"),
  checklist: document.getElementById("checklist"),
  footnote: document.getElementById("footnote"),
};

nodes.refreshButton.addEventListener("click", () => {
  refreshHealth().catch((error) => {
    state.error = error;
    state.loading = false;
    render();
  });
});

bootstrap().catch((error) => {
  state.error = error;
  state.loading = false;
  render();
});

async function bootstrap() {
  state.config = await loadConfig();
  render();
  await refreshHealth();
}

async function loadConfig() {
  for (const path of ["./config.json", "./config.example.json"]) {
    try {
      const response = await fetch(path, { cache: "no-store" });
      if (!response.ok) {
        continue;
      }
      const payload = await response.json();
      return normalizeConfig(payload);
    } catch {
      // Try the fallback file.
    }
  }

  return normalizeConfig(DEFAULT_CONFIG);
}

function normalizeConfig(raw) {
  const backends = Array.isArray(raw?.backends) ? raw.backends : DEFAULT_CONFIG.backends;
  const checklist = Array.isArray(raw?.checklist) ? raw.checklist : DEFAULT_CONFIG.checklist;

  return {
    tribeName: stringOr(raw?.tribeName, DEFAULT_CONFIG.tribeName),
    mvpName: stringOr(raw?.mvpName, DEFAULT_CONFIG.mvpName),
    frontendUrl: stringOr(raw?.frontendUrl, DEFAULT_CONFIG.frontendUrl),
    allowedOrigin: stringOr(raw?.allowedOrigin, stringOr(raw?.frontendUrl, DEFAULT_CONFIG.allowedOrigin)),
    backends: backends.map((backend, index) => ({
      name: stringOr(backend?.name, `Backend ${index + 1}`),
      purpose: stringOr(backend?.purpose, "Integracion de dominio"),
      baseUrl: stringOr(backend?.baseUrl, "https://example.com"),
      healthPath: stringOr(backend?.healthPath, "/api/health"),
      docsPath: stringOr(backend?.docsPath, "/docs"),
      openapiPath: stringOr(backend?.openapiPath, "/v3/api-docs"),
    })),
    checklist: checklist.map((item, index) => ({
      title: stringOr(item?.title, `Paso ${index + 1}`),
      detail: stringOr(item?.detail, ""),
    })),
    demo: {
      notes: stringOr(raw?.demo?.notes, DEFAULT_CONFIG.demo.notes),
    },
  };
}

async function refreshHealth() {
  state.loading = true;
  state.error = null;
  render();

  const checks = await Promise.allSettled(state.config.backends.map((backend) => checkBackend(backend)));
  state.backendChecks = checks.map((item, index) => ({
    backend: state.config.backends[index],
    result: item.status === "fulfilled" ? item.value : { ok: false, status: "error", detail: item.reason?.message ?? "error" },
  }));
  state.loading = false;
  state.updatedAt = new Date();
  render();
}

async function checkBackend(backend) {
  const url = new URL(backend.healthPath || "/api/health", backend.baseUrl).toString();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);

  try {
    const response = await fetch(url, {
      method: "GET",
      mode: "cors",
      signal: controller.signal,
      headers: {
        Accept: "application/json",
      },
    });
    const bodyText = await response.text();
    let body = null;

    try {
      body = JSON.parse(bodyText);
    } catch {
      body = null;
    }

    return {
      ok: response.ok,
      status: response.status,
      detail: inferDetail(response.ok, body),
      url,
      body,
    };
  } catch (error) {
    return {
      ok: false,
      status: error.name === "AbortError" ? "timeout" : "offline",
      detail: error.name === "AbortError" ? "Timeout" : error.message,
      url,
      body: null,
    };
  } finally {
    clearTimeout(timer);
  }
}

function inferDetail(ok, body) {
  if (!ok) {
    return "Health endpoint returned an error";
  }

  if (body && typeof body === "object") {
    if (typeof body.status === "string") {
      return body.status;
    }

    if (typeof body.ok === "boolean") {
      return body.ok ? "ok" : "not ok";
    }
  }

  return "ok";
}

function render() {
  nodes.tribeTitle.textContent = state.config.tribeName;
  nodes.tribeLead.textContent = `${state.config.mvpName} - frontend agnostico y contrato REST de integracion.`;

  const healthy = state.backendChecks.filter((item) => item.result.ok).length;
  const total = state.config.backends.length;
  const label = state.loading
    ? "Verificando"
    : healthy === total && total > 0
      ? "Todo online"
      : healthy > 0
        ? "Parcial"
        : "Atencion";

  nodes.overallPill.className = `pill ${pillClass(label)}`;
  nodes.overallPill.textContent = label;
  nodes.lastUpdated.textContent = state.updatedAt
    ? `Actualizado ${state.updatedAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    : "Sin datos aun";

  nodes.summary.innerHTML = `
    <div class="panel__header">
      <div>
        <div class="panel__kicker">Panorama</div>
        <h2 class="panel__title">La tribu como producto integrado</h2>
        <p class="panel__subtitle">Una unica experiencia web que conversa con dos backends, valida salud y prepara la demo.</p>
      </div>
    </div>
    <div class="panel__inner">
      <div class="metric-grid">
        <div class="metric">
          <div class="metric__label">Backends healthy</div>
          <div class="metric__value">${healthy}/${total}</div>
          <div class="metric__detail">Chequeo remoto sobre <code>GET ${escapeHtml(state.config.backends[0]?.healthPath || "/api/health")}</code> y su par.</div>
        </div>
        <div class="metric">
          <div class="metric__label">Frontend URL</div>
          <div class="metric__value">${escapeHtml(shorten(state.config.frontendUrl, 28))}</div>
          <div class="metric__detail">Origin que debe estar en la allowlist de los dos backends.</div>
        </div>
        <div class="metric">
          <div class="metric__label">Demo focus</div>
          <div class="metric__value">${escapeHtml(state.config.mvpName)}</div>
          <div class="metric__detail">Vision, dominio, despliegue y verificacion antes de exponer la demo.</div>
        </div>
      </div>
    </div>
  `;

  nodes.backends.innerHTML = `
    <div class="panel__header">
      <div>
        <div class="panel__kicker">Backends</div>
        <h2 class="panel__title">Dos APIs, una sola tribu</h2>
        <p class="panel__subtitle">Cada backend debe responder salud, aceptar el origin del frontend y exponer el contrato que necesita la integracion.</p>
      </div>
    </div>
    <div class="panel__inner">
      <div class="backend-list">
        ${state.config.backends
          .map((backend, index) => {
            const result = state.backendChecks[index]?.result;
            const status = result ? resultClass(result) : "status--loading";
            const label = result ? resultLabel(result) : "pending";
            return `
              <article class="backend">
                <div class="backend__top">
                  <div>
                    <div class="backend__name">${escapeHtml(backend.name)}</div>
                    <div class="backend__purpose">${escapeHtml(backend.purpose)}</div>
                  </div>
                  <span class="status ${status}">${escapeHtml(label)}</span>
                </div>
                <div class="backend__meta">
                  <span><strong>Base URL:</strong> ${escapeHtml(backend.baseUrl)}</span>
                  <span><strong>Health:</strong> ${escapeHtml(backend.healthPath || "/api/health")}</span>
                  <span><strong>Last check:</strong> ${escapeHtml(result ? `${result.status} / ${result.detail}` : "pendiente")}</span>
                </div>
                <div class="backend__links">
                  <a class="backend__link" href="${escapeHtml(buildBackendUrl(backend.baseUrl, backend.docsPath))}" target="_blank" rel="noreferrer">Swagger UI</a>
                  <a class="backend__link" href="${escapeHtml(buildBackendUrl(backend.baseUrl, backend.openapiPath))}" target="_blank" rel="noreferrer">OpenAPI JSON</a>
                </div>
              </article>
            `;
          })
          .join("")}
      </div>
    </div>
  `;

  nodes.contract.innerHTML = `
    <div class="panel__header">
      <div>
        <div class="panel__kicker">Contrato</div>
        <h2 class="panel__title">Configuracion minima de la tribu</h2>
        <p class="panel__subtitle">El frontend se adapta a la configuracion del repo y los backends se integran por HTTP/HTTPS.</p>
      </div>
    </div>
    <div class="panel__inner">
      <div class="contract-grid">
        <div class="contract-row">
          <div class="contract-label">Frontend origin</div>
          <div class="contract-value">${escapeHtml(state.config.allowedOrigin)}</div>
        </div>
        <div class="contract-row">
          <div class="contract-label">Smoke script</div>
          <div class="contract-value">scripts/smoke-mvp.sh</div>
        </div>
        <div class="contract-row">
          <div class="contract-label">Docs convention</div>
          <div class="contract-value">Cada backend publica Swagger UI en <code>/docs</code> y el spec en <code>/v3/api-docs</code> (<code>/swagger-ui.html</code> queda como alias de compatibilidad).</div>
        </div>
        <div class="contract-row">
          <div class="contract-label">Verificacion</div>
          <div class="contract-value">GET /api/health en ambos backends, respuesta JSON y CORS permitiendo el origin del frontend.</div>
        </div>
      </div>
    </div>
  `;

  nodes.checklist.innerHTML = `
    <div class="panel__header">
      <div>
        <div class="panel__kicker">Checklist</div>
        <h2 class="panel__title">Antes de la demo</h2>
        <p class="panel__subtitle">El orden importa: vision, modelo, deploy, CORS y smoke. Si falta uno, la demo se rompe en el peor momento.</p>
      </div>
    </div>
    <div class="panel__inner">
      <ul class="checklist-list">
        ${state.config.checklist
          .map(
            (item, index) => `
              <li class="checklist-item">
                <div class="checklist-icon">${index + 1}</div>
                <div>
                  <div class="checklist-title">${escapeHtml(item.title)}</div>
                  <div class="checklist-detail">${escapeHtml(item.detail)}</div>
                </div>
              </li>
            `,
          )
          .join("")}
      </ul>
    </div>
  `;

  nodes.footnote.innerHTML = `
    <strong>Demo note:</strong> ${escapeHtml(state.config.demo?.notes || DEFAULT_CONFIG.demo.notes)}
    ${state.error ? `&nbsp;|&nbsp;<span class="status status--bad">error</span> ${escapeHtml(state.error.message || String(state.error))}` : ""}
  `;
}

function resultClass(result) {
  if (!result.ok) {
    return result.status === "timeout" ? "status--warn" : "status--bad";
  }

  return "status--ok";
}

function resultLabel(result) {
  if (!result.ok) {
    return result.status === "timeout" ? "timeout" : "offline";
  }

  return "ok";
}

function pillClass(label) {
  switch (label) {
    case "Todo online":
      return "pill--good";
    case "Parcial":
      return "pill--warn";
    case "Atencion":
      return "pill--bad";
    default:
      return "";
  }
}

function stringOr(value, fallback) {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function buildBackendUrl(baseUrl, path) {
  return new URL(path || "/", baseUrl).toString();
}

function shorten(value, maxLength) {
  const text = String(value);
  if (text.length <= maxLength) {
    return text;
  }

  return `${text.slice(0, maxLength - 1)}…`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
