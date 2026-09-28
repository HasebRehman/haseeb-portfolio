import http.server
import socketserver
import os
import urllib.parse
import json
import importlib
import email_service

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/api/contact", "/form-process.php", "/form-process"):
            try:
                importlib.reload(email_service)
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                
                # Support JSON and Form-URLEncoded
                content_type = self.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    data = json.loads(body)
                else:
                    parsed_dict = urllib.parse.parse_qs(body)
                    data = {k: v[0] if len(v) == 1 else v for k, v in parsed_dict.items()}

                fname = data.get("fname", "").strip()
                lname = data.get("lname", "").strip()
                phone = data.get("phone", "").strip()
                email = data.get("email", "").strip()
                message = data.get("message", "").strip()

                if not email or not fname:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "message": "First name and email are required."}).encode("utf-8"))
                    return

                success, msg = email_service.send_contact_emails(fname, lname, phone, email, message)

                if success:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": True,
                        "message": "Thank you! Your message has been sent successfully. Check your email for confirmation."
                    }).encode("utf-8"))
                else:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "message": msg}).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": f"Server error: {str(e)}"}).encode("utf-8"))
            return

        return super().do_POST()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 301 Redirect index.html or index to /
        if path in ("/index.html", "/index"):
            query_str = f"?{parsed.query}" if parsed.query else ""
            self.send_response(301)
            self.send_header("Location", f"/{query_str}")
            self.end_headers()
            return

        # 301 Redirect .html extensions to clean URLs (e.g. /about.html -> /about)
        if path.endswith(".html") and path != "/404.html":
            clean_path = path[:-5]
            query_str = f"?{parsed.query}" if parsed.query else ""
            self.send_response(301)
            self.send_header("Location", f"{clean_path}{query_str}")
            self.end_headers()
            return

        return super().do_GET()

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/index.html", "/index"):
            query_str = f"?{parsed.query}" if parsed.query else ""
            self.send_response(301)
            self.send_header("Location", f"/{query_str}")
            self.end_headers()
            return

        if path.endswith(".html") and path != "/404.html":
            clean_path = path[:-5]
            query_str = f"?{parsed.query}" if parsed.query else ""
            self.send_response(301)
            self.send_header("Location", f"{clean_path}{query_str}")
            self.end_headers()
            return

        return super().do_HEAD()

    def translate_path(self, path):
        translated = super().translate_path(path)
        if not os.path.exists(translated):
            if os.path.exists(translated + ".html"):
                return translated + ".html"
        return translated

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            error_page = os.path.join(DIRECTORY, "404.html")
            if os.path.exists(error_page):
                self.send_response(404)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                with open(error_page, "rb") as f:
                    self.wfile.write(f.read())
                return
        super().send_error(code, message, explain)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving at http://localhost:{PORT} with clean URLs, custom 404, and /api/contact handler...")
        httpd.serve_forever()
