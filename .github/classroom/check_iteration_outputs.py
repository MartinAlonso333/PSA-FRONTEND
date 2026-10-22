#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path.cwd()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_iteration_outputs.py <starter|integracion-01|integracion-02>")

    mode = sys.argv[1]
    common_checks()

    if mode == "starter":
        starter_checks()
    elif mode == "integracion-01":
        starter_checks()
        integracion_01_checks()
    elif mode == "integracion-02":
        starter_checks()
        integracion_02_checks()
    else:
        raise SystemExit(f"unsupported mode: {mode}")


def common_checks() -> None:
    require_markdown_sections(
        "README.md",
        [
            "## Entregables de tribu",
            "## Estructura",
            "## Como se trabaja",
            "## Verificacion rapida",
            "## Idea tecnica",
        ],
        min_length=500,
    )
    require_markdown_sections(
        "docs/operacion/guia-tribu-template.md",
        [
            "## Proceso de trabajo",
            "## Configuracion",
            "## Verificaciones",
            "## Despliegue",
            "## Demo",
            "## Problemas frecuentes",
        ],
        min_length=500,
    )
    require_markdown_sections("iteraciones/README.md", ["## Iteraciones de la tribu"], min_length=140)
    require_markdown_sections("entregas/README.md", ["##"], min_length=120)
    require_markdown_sections("iteraciones/integracion-01.md", ["## Objetivo", "## Entrega asociada", "## Entregables esperados", "## Criterio de cierre"], min_length=220)
    require_markdown_sections("iteraciones/integracion-02.md", ["## Objetivo", "## Entrega asociada", "## Entregables esperados", "## Criterio de cierre"], min_length=220)
    require_json_config("config.json")
    require_json_config("config.example.json")
    require_index_contract()
    require_app_contract()
    require_script_contract("scripts/smoke_mvp.py", ["TRIBU_FRONTEND_URL", "Access-Control-Allow-Origin", "config must define exactly two backends"])


def starter_checks() -> None:
    require_files(
        [
            "scripts/dev-server.sh",
            "scripts/smoke-mvp.sh",
            "scripts/smoke_mvp.py",
            "scripts/preflight-integracion-01.sh",
            "scripts/preflight-integracion-02.sh",
            ".github/workflows/classroom.yml",
            ".github/classroom/run_preflight.sh",
            ".github/classroom/check_required_files.sh",
            ".github/classroom/check_forbidden_files.sh",
            ".github/classroom/check_agents_contract.sh",
            ".github/classroom/check_feedback_guidance.sh",
            ".github/classroom/check_iteration_outputs.py",
        ]
    )
    require_markdown_sections(
        "docs/vision/vision-tribu-template.md",
        [
            "## Nombre de la tribu",
            "## Problema u oportunidad",
            "## Resumen ejecutivo",
            "## Alcance del MVP",
            "## Integracion con los squads",
            "## Criterios de exito",
            "## Dudas abiertas",
        ],
        min_length=420,
    )
    require_markdown_sections(
        "docs/analisis/modelo-dominio-template.md",
        [
            "## Alcance del modelo",
            "## Inputs usados",
            "## Historias priorizadas tomadas como base",
            "## Clases conceptuales",
            "## Asociaciones",
            "## Atributos",
            "## Diagrama",
            "## Trazabilidad",
            "## Fuera de alcance y exclusiones",
            "## Dudas abiertas",
        ],
        min_length=420,
    )
    require_plantuml_template("docs/analisis/modelo-dominio-template.puml")
    require_markdown_sections(
        "docs/arquitectura/api-integracion-template.md",
        [
            "## Alcance del API",
            "## Endpoints",
            "## Contratos principales",
            "## Errores y validaciones",
            "## Integracion y CORS",
            "## Dudas abiertas",
        ],
        min_length=360,
    )


def integracion_01_checks() -> None:
    require_markdown_sections(
        "entregas/integracion-01-template.md",
        [
            "## Entrega y alcance",
            "## Artefactos consolidados",
            "## Cambios principales",
            "## Decisiones tomadas",
            "## Riesgos y pendientes",
            "## Proximos pasos",
        ],
        min_length=180,
    )


def integracion_02_checks() -> None:
    require_markdown_sections(
        "entregas/integracion-02-template.md",
        [
            "## Entrega y alcance",
            "## Artefactos consolidados",
            "## Cambios principales",
            "## Decisiones tomadas",
            "## Evidencia de despliegue o ejecucion demostrable",
            "## Riesgos y pendientes",
            "## Proximos pasos",
        ],
        min_length=220,
    )
    require_script_contract("scripts/smoke-mvp.sh", ["smoke_mvp.py"])
    require_script_contract("scripts/dev-server.sh", ["http.server", "4173"])


def require_files(paths: list[str]) -> None:
    missing = [path for path in paths if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f"missing required files: {', '.join(missing)}")


def require_markdown_sections(path: str, sections: list[str], *, min_length: int = 0) -> None:
    text = require_file(path).read_text(encoding="utf-8")
    if len(text.strip()) < min_length:
        raise SystemExit(f"file too short: {path}")
    for section in sections:
        if section not in text:
            raise SystemExit(f"missing section {section!r} in {path}")
    require_without_placeholder_markers(path)


def require_json_config(path: str) -> None:
    payload = json.loads(require_file(path).read_text(encoding="utf-8"))
    if "frontendUrl" not in payload:
        raise SystemExit(f"{path} must define frontendUrl")
    if "backends" not in payload or not isinstance(payload["backends"], list) or len(payload["backends"]) != 2:
        raise SystemExit(f"{path} must define exactly two backends")

    for index, backend in enumerate(payload["backends"], start=1):
        for key in ("name", "baseUrl", "healthPath"):
            if key not in backend or not str(backend[key]).strip():
                raise SystemExit(f"{path} backend {index} is missing {key}")


def require_index_contract() -> None:
    text = require_file("index.html").read_text(encoding="utf-8")
    for token in ("styles.css", "app.js", "id=\"refresh-button\"", "id=\"summary\"", "id=\"backends\"", "id=\"contract\"", "id=\"checklist\""):
        if token not in text:
            raise SystemExit(f"index.html is missing {token!r}")


def require_app_contract() -> None:
    text = require_file("app.js").read_text(encoding="utf-8")
    for token in ("loadConfig", "refreshHealth", "checkBackend", "fetch(", "config.json", "config.example.json"):
        if token not in text:
            raise SystemExit(f"app.js is missing {token!r}")


def require_script_contract(path: str, tokens: list[str]) -> None:
    text = require_file(path).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            raise SystemExit(f"{path} is missing {token!r}")


def require_plantuml_template(path: str) -> None:
    text = require_file(path).read_text(encoding="utf-8")
    for token in ("@startuml", "@enduml"):
        if token not in text:
            raise SystemExit(f"{path} must define {token}")
    if "class " not in text:
        raise SystemExit(f"{path} must declare at least one class")
    require_without_placeholder_markers(path)


def require_file(path: str) -> Path:
    target = ROOT / path
    if not target.is_file():
        raise SystemExit(f"missing file: {path}")
    return target


def require_without_placeholder_markers(path: str) -> None:
    text = require_file(path).read_text(encoding="utf-8")
    patterns = [
        r"(?m)^\s*\.\.\.\s*$",
        r"(?m)^\s*[-*]\s+\.\.\.\s*$",
        r"(?m)^\s*\d+\.\s+\.\.\.\s*$",
        r"(?m)^\|(?:[^|\n]*\.\.\.[^|\n]*\|){2,}\s*$",
    ]
    if any(re.search(pattern, text) for pattern in patterns):
        raise SystemExit(f"placeholder content detected in {path}")


if __name__ == "__main__":
    main()
