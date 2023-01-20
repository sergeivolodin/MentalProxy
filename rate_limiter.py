from threading import Lock
from time import time


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
    """Allow 1 timeline call per 60 seconds."""
    
    TIMELINE_PERIOD = 60
    
    def __init__(self):
        super(RateLimiterPostsPerMinute, self).__init__()
        self.timeline_lock = Lock()
        self.last_timeline_request = None
    
    @property
    def notifications_remaining_time(self):
        t_now = time()
        
        self.timeline_lock.acquire()
        t = self.last_timeline_request
        self.timeline_lock.release()
        
        if t is None:
            return None
        
        return (self.TIMELINE_PERIOD - t_now + t)
    
    def timeline_request_ok(self):
        t_now = time()
        
        self.timeline_lock.acquire()
        t_last = self.last_timeline_request
        self.timeline_lock.release()
        
        if t_last is None:
            ans = True
        else:
            # 20 posts (1 batch)
            # per 60 seconds
            ans = t_now - t_last >= self.TIMELINE_PERIOD
    
        if ans:
            self.timeline_lock.acquire()
            self.last_timeline_request = t_now
            self.timeline_lock.release()
        
        return ans
    
class RateLimiterNotificationAtRoundTime(RateLimiter):
    """Queue notifications and show them at HH:00 and HH:30 only."""
        
    def __init__(self):
        super(RateLimiterNotificationAtRoundTime, self).__init__()
        self.notification_lock = Lock()
        self.last_notification_ok = None
    
    def notifications_request_ok(self):
        t_now = time()
        
        self.notification_lock.acquire()
        t = self.last_notification_ok
        self.notification_lock.release()
        
        if t is None:
            ans = True
        else:
            dt = 60 * 30
            # in the next part of the hour
            ans = int(t_now) // dt != int(t) % dt
        
        if ans:
            self.notification_lock.acquire()
            self.last_notification_ok = t_now
            self.notification_lock.release()
        
        return ans
    
class RateLimiterPostsNotifications(RateLimiterNotificationAtRoundTime, RateLimiterPostsPerMinute):
    pass