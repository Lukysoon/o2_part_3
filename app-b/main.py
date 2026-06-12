"""App B (backend) - hello world HTTP server.

Vraci JSON se jmenem podu (hostname) a verzi, aby bylo videt:
 - load-balancing mezi replikami (hostname se strida)
 - prubeh rolling update (verze se postupne meni v1 -> v2)
"""
import json
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.environ.get("APP_VERSION", "v1")
PORT = int(os.environ.get("PORT", "8080"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({
            "message": "Hello from app B",
            "pod": socket.gethostname(),
            "version": VERSION,
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[app-b {VERSION}] {self.address_string()} {fmt % args}")


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
