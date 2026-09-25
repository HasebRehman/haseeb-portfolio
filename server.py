import http.server
import socketserver
import os
import urllib.parse

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

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
        print(f"Serving at http://localhost:{PORT} with clean URLs and custom 404 handler...")
        httpd.serve_forever()
