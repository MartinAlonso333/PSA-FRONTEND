#!/usr/bin/env python3

from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("PORT", "4174"))
BASE_URL = f"http://127.0.0.1:{PORT}"
BACKEND_1_URL = os.environ.get("TRIBU_BACKEND_1_URL", os.environ.get("TRIBU_BACKEND_URL", "http://127.0.0.1:8081"))
BACKEND_2_URL = os.environ.get("TRIBU_BACKEND_2_URL", os.environ.get("TRIBU_BACKEND_URL", BACKEND_1_URL))


def build_config() -> dict[str, object]:
    return {
        "tribeName": "Tribu A",
        "mvpName": "MVP integrado",
        "frontendUrl": BASE_URL,
        "allowedOrigin": BASE_URL,
        "backends": [
            {
                "name": "Squad 1 backend",
                "purpose": "Dominio A",
                "baseUrl": f"{BASE_URL}/backend-1/",
                "healthPath": "api/health",
                "docsPath": "docs",
                "openapiPath": "v3/api-docs",
            },
            {
                "name": "Squad 3 backend",
                "purpose": "Dominio B",
                "baseUrl": f"{BASE_URL}/backend-2/",
                "healthPath": "api/health",
                "docsPath": "docs",
                "openapiPath": "v3/api-docs",
            },
        ],
        "checklist": [
            {"title": "Vision integrada", "detail": "Una sola narrativa de producto, MVP y fuera de alcance."},
            {"title": "Modelo de dominio", "detail": "Conceptual, compartido y sin vocabulario tecnico."},
            {"title": "Frontend desplegado", "detail": "Una URL publica que presenta el estado de la tribu."},
            {"title": "Backends accesibles", "detail": "Ambos servicios responden `GET /api/health` por HTTPS."},
            {"title": "CORS verificado", "detail": "Los dos backends aceptan el origin del frontend."},
            {"title": "Demo lista", "detail": "Smoke test y guion de demostracion antes de exponer."},
        ],
        "demo": {
            "notes": "Antes de mostrar, correr el smoke de produccion y verificar que las dos APIs sigan vivas.",
        },
    }


class DevIntegrationHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self._serve_generated_config():
            return
        if self.path == "/backend-1":
            self.send_response(301)
            self.send_header("Location", "/backend-1/")
            self.end_headers()
            return
        if self.path == "/backend-2":
            self.send_response(301)
            self.send_header("Location", "/backend-2/")
            self.end_headers()
            return
        if self._proxy_backend():
            return
        super().do_GET()

    def do_HEAD(self) -> None:  # noqa: N802
        if self._serve_generated_config(head_only=True):
            return
        if self.path == "/backend-1":
            self.send_response(301)
            self.send_header("Location", "/backend-1/")
            self.end_headers()
            return
        if self.path == "/backend-2":
            self.send_response(301)
            self.send_header("Location", "/backend-2/")
            self.end_headers()
            return
        if self._proxy_backend(head_only=True):
            return
        super().do_HEAD()

    def _serve_generated_config(self, head_only: bool = False) -> bool:
        if self.path not in {"/config.json", "/config.example.json"}:
            return False

        body = json.dumps(build_config(), ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)
        return True

    def _proxy_backend(self, head_only: bool = False) -> bool:
        route = self._matched_route()
        if route is None:
            return False

        prefix, upstream = route
        request_path = self.path[len(prefix) :]
        if request_path == "":
            request_path = "/"

        parts = urlsplit(request_path)
        upstream_url = upstream.rstrip("/") + parts.path
        if parts.query:
            upstream_url += f"?{parts.query}"

        request = Request(upstream_url, method="HEAD" if head_only else "GET")
        request.add_header("Accept", "*/*")

        try:
            with urlopen(request) as response:
                body = b"" if head_only else response.read()
                if not head_only and self._should_rewrite_openapi(request_path):
                    body = self._rewrite_openapi_servers(body, prefix)
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() in {"transfer-encoding", "connection", "content-length"}:
                        continue
                    if body and self._should_rewrite_openapi(request_path) and key.lower() == "content-type":
                        continue
                    self.send_header(key, value)
                if body and self._should_rewrite_openapi(request_path):
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if not head_only:
                    self.wfile.write(body)
        except HTTPError as error:
            body = b"" if head_only else error.read()
            self.send_response(error.code)
            for key, value in error.headers.items():
                if key.lower() in {"transfer-encoding", "connection", "content-length"}:
                    continue
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if not head_only and body:
                self.wfile.write(body)
        except URLError as error:
            body = str(error).encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if not head_only:
                self.wfile.write(body)

        return True

    def _should_rewrite_openapi(self, request_path: str) -> bool:
        path = request_path.split("?", 1)[0].rstrip("/")
        return path.endswith("/v3/api-docs")

    def _rewrite_openapi_servers(self, body: bytes, prefix: str) -> bytes:
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return body

        if not isinstance(payload, dict):
            return body

        payload["servers"] = [{"url": prefix}]
        return json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def _matched_route(self) -> tuple[str, str] | None:
        if self.path.startswith("/backend-1/"):
            return "/backend-1", BACKEND_1_URL
        if self.path.startswith("/backend-2/"):
            return "/backend-2", BACKEND_2_URL
        return None

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), lambda *args, **kwargs: DevIntegrationHandler(*args, directory=str(ROOT), **kwargs))
    print(f"Serving tribu integration front on http://127.0.0.1:{PORT}")
    print(f"Backend 1 upstream: {BACKEND_1_URL}")
    print(f"Backend 2 upstream: {BACKEND_2_URL}")
    server.serve_forever()


if __name__ == "__main__":
    main()
