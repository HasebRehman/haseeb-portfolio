from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Ensure parent directory is in path for chatbot_service
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import chatbot_service

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
            data = json.loads(body) if body else {}

            message = data.get("message", "").strip()
            # User identification (client IP or token)
            forwarded_for = self.headers.get("X-Forwarded-For", "")
            client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (self.client_address[0] if self.client_address else "127.0.0.1")
            user_id = data.get("user_id") or client_ip
            history = data.get("history", [])

            result = chatbot_service.process_chat(message, user_id, history)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

        except Exception as e:
            # Fallback to local default - zero errors shown to user
            fallback_answer = chatbot_service.get_default_answer("general")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "answer": fallback_answer,
                "provider": "local-fallback"
            }).encode("utf-8"))
