from threading import Lock


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