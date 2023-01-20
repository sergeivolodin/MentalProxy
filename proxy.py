from base_reverse_proxy import BaseReverseProxyHandler
from http.server import ThreadingHTTPServer
from threading import Lock

# configuration
destination_schema = 'https'
destination_host = 'dair-community.social'
listen_port = 8083

class MastodonEthicalProxy(BaseReverseProxyHandler):
    """Ethical proxy."""
    
    def disable_websockets(self, response):
        """Disable websockets to have no push notifications (only pull)."""
        if 'text/html' not in response.headers.get('content-type', ''):
            return
        to_replace = ('wss://' + self.get_destination_host()).encode('utf-8')
        response._content = response.content.replace(to_replace, b'wss://0.0.0.0')
    
    def process_response(self, response):
        """Process the response from the destination."""
        super(MastodonEthicalProxy, self).process_response(response)
        self.disable_websockets(response)

def run():
    """Run the server."""
    server_address = ('', listen_port)
    handler_class = MastodonEthicalProxy.point_to(destination_schema, destination_host)
    httpd = ThreadingHTTPServer(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()