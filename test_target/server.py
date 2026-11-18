import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class TestVulnerableAppHandler(BaseHTTPRequestHandler):
    """
    Lightweight, deliberately vulnerable test target for controlled, safe
    scanner integration testing (OWASP ZAP and Nuclei).
    """
    server_version = "SecureMind-TrainingApp/1.0"
    sys_version = ""

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "service": "test_target"}')
            return

        if path == "/.well-known/securemind-challenge.txt":
            # Test challenge endpoint
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"securemind-verify=training-app-token-12345\n")
            return

        if path == "/search":
            query = params.get("q", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            # Intentionally omitting Content-Security-Policy & X-Frame-Options
            self.end_headers()
            html = f"""<!DOCTYPE html>
<html>
<head><title>Training App - Search</title></head>
<body>
    <h1>Search Portal</h1>
    <p>Results for query: {query}</p>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        # Default root endpoint
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        # Intentionally missing CSP, HSTS, X-Content-Type-Options
        self.end_headers()
        html = """<!DOCTYPE html>
<html>
<head><title>SecureMind Training Target</title></head>
<body>
    <h1>Welcome to SecureMind AI Test Target</h1>
    <p>This is a safe, offline application used strictly for verifying scanner integrations.</p>
    <a href="/search?q=test">Search Portal</a>
</body>
</html>"""
        self.wfile.write(html.encode("utf-8"))

def run(port=9090):
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, TestVulnerableAppHandler)
    print(f"Test target application running on http://0.0.0.0:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9090
    run(port)
