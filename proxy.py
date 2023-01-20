from base_reverse_proxy import BaseReverseProxyHandler
from http.server import ThreadingHTTPServer
from threading import Lock

# configuration
destination_schema = 'https'
destination_host = 'dair-community.social'
listen_port = 8083

class RateLimiter():
    def notifications_request_ok():
        return False
        pass
    
    def timeline_request_ok():
        return False
        pass

class BaseMastodonEthicalProxy(BaseReverseProxyHandler):
    """Ethical proxy."""
    
    @property
    def rate_limiter(self):
        raise NotImplemented('Please use with_limit()')
    
    @classmethod
    def with_limit(cls, rlim):
        """Add a rate limiter for all threads."""
        if rlim is None:
            raise ValueError("Please supply a ratelimiter")
        
        class MastodonEthicalProxy(cls):
            @property
            def rate_limiter(self):
                return rlim
        
        return MastodonEthicalProxy
    
    def filter_incoming_request(self):
        print(self.path)
        
        if 'api/v1/notifications' in self.path and not self.rate_limiter.notifications_request_ok():
            self.send_error(403)
            
        if '/api/v1/timelines/' in self.path and not self.rate_limiter.timeline_request_ok():
            self.send_error(403)
    
    def disable_websockets(self, response):
        """Disable websockets to have no push notifications (only pull)."""
        if 'text/html' not in response.headers.get('content-type', ''):
            return
        to_replace = ('wss://' + self.destination_host).encode('utf-8')
        response._content = response.content.replace(to_replace, b'wss://0.0.0.0')
    
    def process_response(self, response):
        """Process the response from the destination."""
        super(BaseMastodonEthicalProxy, self).process_response(response)
        self.disable_websockets(response)

def run():
    """Run the server."""
    server_address = ('', listen_port)
    ratelimiter = RateLimiter()
    handler_class = BaseMastodonEthicalProxy\
        .point_to(destination_schema, destination_host)\
        .with_limit(ratelimiter)
    httpd = ThreadingHTTPServer(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()