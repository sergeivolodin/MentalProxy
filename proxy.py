from base_reverse_proxy import BaseReverseProxyHandler
from http.server import ThreadingHTTPServer

# configuration
destination_schema = 'https'
destination_host = 'dair-community.social'
listen_port = 8083

def run():
    """Run the server."""
    server_address = ('', listen_port)
    handler_class = BaseReverseProxyHandler.factory(destination_schema, destination_host)
    httpd = ThreadingHTTPServer(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()