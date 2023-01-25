from mentalproxy.base_reverse_proxy import BaseReverseProxyHandler
from mentalproxy.http_tools import HTTPTools


class BaseTwitterEthicalProxy(BaseReverseProxyHandler, HTTPTools):
    """Ethical proxy."""
    
    @property
    def rate_limiter(self):
        raise NotImplemented('Please use with_limit()')
    
    @property
    def destination_schema(self):
        return 'https'
    
    @property
    def destination_host(self):
        return 'mobile.twitter.com'
    
    @property
    def delete_response_headers(self):
        p = super().delete_response_headers
        p.append('cross-origin-opener-policy')
        p.append('cross-origin-embedder-policy')
        return p
    
    def remove_cookie_security(self, response_headers):
        """Remove the secure parameter from set-cookie headers."""
        subs = 'Domain=.twitter.com; Secure; SameSite=None'
        if 'set-cookie' in response_headers:
            if response_headers['set-cookie'].endswith(subs):
                response_headers['set-cookie'] = response_headers['set-cookie'][:-len(subs)]
    
    @classmethod
    def with_limit(cls, rlim):
        """Add a rate limiter for all threads."""
        if rlim is None:
            raise ValueError("Please supply a ratelimiter")
        
        class TwitterEthicalProxy(cls):
            @property
            def rate_limiter(self):
                return rlim
        
        return TwitterEthicalProxy
    
    def filter_incoming_request(self):
        pass
        # if 'api/v1/notifications' in self.path and not self.rate_limiter.notifications_request_ok():
        #     self.send_empty_json_array()

        #     # self.send_error(403, "Notifications muted for mental wellbeing")
        #     return True
            
        # if '/api/v1/timelines/' in self.path and not self.rate_limiter.timeline_request_ok():
            
        #     # send a 403 with a message
        #     self.send_error(403, f"Timeline paused for {int(self.rate_limiter.notifications_remaining_time)} more seconds...")
            
        #     # send an empty json (no error, shows as empty)
        #     # self.send_empty_json()
        #     return True
    
    def process_response(self, response):
        """Process the response from the destination."""
        super(BaseTwitterEthicalProxy, self).process_response(response)
        self.disable_websockets(response)