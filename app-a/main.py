"""App A (frontend) - pri kazdem requestu zavola app B pres service DNS.

Demonstruje komunikaci mezi castmi aplikace: "service-b" je DNS jmeno
Kubernetes Service, ktera load-balancuje na pody app B na ruznych uzlech.
"""
import json
import os
import socket
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BACKEND_URL = os.environ.get("BACKEND_URL", "http://service-b:8080")
PORT = int(os.environ.get("PORT", "8080"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # readiness probe nesmi zaviset na dostupnosti B
        if self.path == "/healthz":
            self._respond(200, {"status": "ok"})
            return
        try:
            with urllib.request.urlopen(BACKEND_URL, timeout=3) as resp:
                backend = json.loads(resp.read())
            status = 200
        except Exception as exc:
            backend = {"error": str(exc)}
            status = 502
        self._respond(status, {
            "message": "Hello from app A",
            "pod": socket.gethostname(),
            "backend_response": backend,
        })

    def _respond(self, status, payload):
        body = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[app-a] {self.address_string()} {fmt % args}")


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
