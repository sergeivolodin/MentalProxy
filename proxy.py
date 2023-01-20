from http.server import HTTPServer, HTTPStatus
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer

# configuration
destination_host = 'dair-community.social'
listen_port = 8080


class ReverseProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        ctype = 'text/html'
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", '123')
        # self.send_header("Last-Modified",
        # self.date_time_string(fs.st_mtime))
        self.end_headers()
        self.wfile.write(b'Hello world')


def run(server_class=HTTPServer, handler_class=ReverseProxyHandler):
    server_address = ('', listen_port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()