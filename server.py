import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # normalize path
        path = self.translate_path(self.path)
        if not os.path.exists(path):
            # Render custom 404.html
            error_page = os.path.join(DIRECTORY, "404.html")
            if os.path.exists(error_page):
                self.send_response(404)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                with open(error_page, "rb") as f:
                    self.wfile.write(f.read())
                return
        return super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving at http://localhost:{PORT} with custom 404 handler...")
        httpd.serve_forever()
