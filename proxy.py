from base_reverse_proxy import BaseReverseProxyHandler
from http.server import ThreadingHTTPServer
from threading import Lock

# configuration
destination_schema = 'https'
destination_host = 'dair-community.social'
listen_port = 8083

class RateLimiter():
    """Limit the rate of messages and notifications."""
    
    # todo: make it per-account rather than global
    
    def notifications_request_ok(self):
        raise NotImplementedError
    
    def timeline_request_ok(self):
        raise NotImplementedError
    
    
class RateLimiterAlwaysYes(RateLimiter):
    def notifications_request_ok(self):
        return True
    
    def timeline_request_ok(self):
        return True


class RateLimiterAlwaysNo(RateLimiter):
    def notifications_request_ok(self):
        return False
    
    def timeline_request_ok(self):
        return False
    

class RateLimiterPostsPerMinute(RateLimiter):
    def timeline_request_ok(self):
        return False

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
    
    def send_empty_json(self):
        """Send an empty json response."""
        self.send_header('content-type', 'application/json')
        self.send_header('content-length', 2)
        self.wfile.write(b'[]')
    
    def filter_incoming_request(self):
        if 'api/v1/notifications' in self.path and not self.rate_limiter.notifications_request_ok():
            self.send_error(403, "Notifications muted for mental wellbeing")
            return True
            
        if '/api/v1/timelines/' in self.path and not self.rate_limiter.timeline_request_ok():
            
            # send a 403 with a message
            # self.send_error(403, "Timeline paused for mental wellbeing")
            
            # send an empty json (no error, shows as empty)
            self.send_empty_json()
            return True
    
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
    ratelimiter = RateLimiterAlwaysNo()
    handler_class = BaseMastodonEthicalProxy\
        .point_to(destination_schema, destination_host)\
        .with_limit(ratelimiter)
    httpd = ThreadingHTTPServer(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()