from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import os
import sys

# Ensure parent directory is in path for email_service
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from email_service import send_contact_emails

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            # Parse form data or json
            data = {}
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

            success, msg = send_contact_emails(fname, lname, phone, email, message)

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
