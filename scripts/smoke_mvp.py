#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Backend:
    name: str
    base_url: str
    health_path: str

    @property
    def health_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/{self.health_path.lstrip('/')}"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config = load_config(repo_root / "config.json", repo_root / "config.example.json")

    frontend_url = os.environ.get("TRIBU_FRONTEND_URL", config["frontendUrl"])
    allowed_origin = os.environ.get("TRIBU_ALLOWED_ORIGIN", config.get("allowedOrigin", frontend_url))
    backends = [
        Backend(
            name=backend.get("name", f"Backend {index + 1}"),
            base_url=os.environ.get(f"TRIBU_BACKEND_{index + 1}_URL", backend["baseUrl"]),
            health_path=backend.get("healthPath", "/api/health"),
        )
        for index, backend in enumerate(config["backends"])
    ]

    smoke_frontend(frontend_url)
    for backend in backends:
        smoke_backend(backend, allowed_origin=allowed_origin)

    print("smoke ok")


def load_config(primary: Path, fallback: Path) -> dict[str, Any]:
    for path in (primary, fallback):
        if path.is_file():
            return validate_config(json.loads(path.read_text(encoding="utf-8")))
    raise SystemExit(f"missing config file: {primary} or {fallback}")


def validate_config(payload: dict[str, Any]) -> dict[str, Any]:
    if "frontendUrl" not in payload:
        raise SystemExit("config is missing frontendUrl")
    if "backends" not in payload or not isinstance(payload["backends"], list) or len(payload["backends"]) != 2:
        raise SystemExit("config must define exactly two backends")
    return payload


def smoke_frontend(frontend_url: str) -> None:
    status, body, _headers = request(frontend_url)
    if status != 200:
        raise SystemExit(f"frontend returned {status} at {frontend_url}")
    if "TPG Tribu" not in body:
        raise SystemExit("frontend page does not look like the tribu starter")


def smoke_backend(backend: Backend, *, allowed_origin: str) -> None:
    status, body, headers = request(backend.health_url, origin=allowed_origin)
    if status != 200:
        raise SystemExit(f"{backend.name} returned {status} at {backend.health_url}")

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{backend.name} health is not valid JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise SystemExit(f"{backend.name} health must return a JSON object")

    cors = headers.get("Access-Control-Allow-Origin")
    if cors not in {allowed_origin, "*"}:
        raise SystemExit(f"{backend.name} CORS does not allow {allowed_origin!r}: {cors!r}")


def request(url: str, *, origin: str | None = None) -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url, headers={"Accept": "application/json, text/html;q=0.9"})
    if origin:
        req.add_header("Origin", origin)

    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            body = response.read().decode("utf-8", errors="replace")
            headers = {key: value for key, value in response.headers.items()}
            return response.status, body, headers
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        headers = {key: value for key, value in exc.headers.items()}
        return exc.code, body, headers
    except urllib.error.URLError as exc:
        raise SystemExit(f"cannot reach {url}: {exc.reason}") from exc


if __name__ == "__main__":
    main()

