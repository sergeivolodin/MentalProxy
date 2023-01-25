from mentalproxy.base_reverse_proxy import BaseReverseProxyHandler
from mentalproxy.http_tools import HTTPTools


class BaseMastodonEthicalProxy(BaseReverseProxyHandler, HTTPTools):
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
        if 'api/v1/notifications' in self.path and not self.rate_limiter.notifications_request_ok():
            self.send_empty_json_array()

            # self.send_error(403, "Notifications muted for mental wellbeing")
            return True
            
        if '/api/v1/timelines/' in self.path and not self.rate_limiter.timeline_request_ok():
            
            # send a 403 with a message
            self.send_error(403, f"Timeline paused for {int(self.rate_limiter.notifications_remaining_time)} more seconds...")
            
            # send an empty json (no error, shows as empty)
            # self.send_empty_json()
            return True
    
    def process_response(self, response):
        """Process the response from the destination."""
        super(BaseMastodonEthicalProxy, self).process_response(response)
        self.disable_websockets(response)