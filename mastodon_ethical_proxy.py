from base_reverse_proxy import BaseReverseProxyHandler


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
            self.send_empty_json()

            # self.send_error(403, "Notifications muted for mental wellbeing")
            return True
            
        if '/api/v1/timelines/' in self.path and not self.rate_limiter.timeline_request_ok():
            
            # send a 403 with a message
            self.send_error(403, f"Timeline paused for {int(self.rate_limiter.notifications_remaining_time)} more seconds...")
            
            # send an empty json (no error, shows as empty)
            # self.send_empty_json()
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