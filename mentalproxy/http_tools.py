from http.server import BaseHTTPRequestHandler
import json


class HTTPTools(BaseHTTPRequestHandler):
    """Helper methods used in reverse proxy classes."""

    def disable_websockets(self, response):
        """Disable websockets to have no push notifications (only pull)."""
        if 'text/html' not in response.headers.get('content-type', ''):
            return
        to_replace = ('wss://' + self.destination_host).encode('utf-8')
        response._content = response.content.replace(to_replace, b'wss://0.0.0.0')
    
    def send_json(self, data):
        """Send an empty json response."""
        s = json.dumps(data).encode('utf-8')
        self.send_response(200, 'OK')
        self.send_header('content-type', 'application/json; charset=utf-8')
        self.send_header('content-length', len(s))
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())
        self.end_headers()
        self.wfile.write(s)

    def send_empty_json_array(self):
        """Send an empty json response."""
        self.send_json([])