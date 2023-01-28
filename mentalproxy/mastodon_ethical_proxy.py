from mentalproxy.base_reverse_proxy import BaseReverseProxyHandler
from mentalproxy.http_tools import HTTPTools
import json


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
    
    def get_is_path_manytoots(self, profile_maxid_required=True):
        c1 = '/api/v1/accounts/' in self.path and 'statuses' in self.path
        if profile_maxid_required:
            c1 = c1 and 'max_id' in self.path
        c2 = '/api/v1/timelines/' in self.path
        return c1 or c2
    
    @property
    def is_path_manytoots(self):
        return self.get_is_path_manytoots()
    
    def is_path_notifications(self):
        return 'api/v1/notifications' in self.path
    
    def reduce_toot_count(self, response, limit=10):
        if not self.get_is_path_manytoots(profile_maxid_required=False):
            return
        assert isinstance(limit, int), limit
        data = response.content
        data = data.decode('utf-8')
        data = json.loads(data)
        data = data[:limit]
        data = json.dumps(data)
        data = data.encode('utf-8')
        response._content = data
        
        print(self.path, 'reduced toot count')
        
    
    def filter_incoming_request(self):
        if self.is_path_notifications and not self.rate_limiter.notifications_request_ok():
            self.send_empty_json_array()

            # self.send_error(403, "Notifications muted for mental wellbeing")
            return True
            
        if self.is_path_manytoots and not self.rate_limiter.timeline_request_ok():
            
            # send a 403 with a message
            self.send_error(403, f"Timeline paused for {int(self.rate_limiter.notifications_remaining_time)} more seconds...")
            
            # send an empty json (no error, shows as empty)
            # self.send_empty_json()
            return True
    
    def process_response(self, response):
        """Process the response from the destination."""
        super(BaseMastodonEthicalProxy, self).process_response(response)
        self.disable_websockets(response)
        self.reduce_toot_count(response)