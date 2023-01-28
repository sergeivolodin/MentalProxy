from mentalproxy.base_reverse_proxy import BaseReverseProxyHandler
from mentalproxy.http_tools import HTTPTools
import json
from requests import Response
from datetime import timezone, datetime
import threading


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
    
    def insert_pause_toot(self, timeout=60):
        
        if not hasattr(self, 'lock_threading'):
            self.lock_threading = threading.Lock()
            
        with self.lock_threading:
            if not hasattr(self, 'last_toot_id'):
                self.last_toot_id = 0
            
            id_ = self.last_toot_id    
            
            self.last_toot_id += 1
        
        uri = f"http://{self.proxy_host}"
        
        print('Returning ID', id_)
        
        return {
            "id": str(id_),
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "in_reply_to_id": None,
            "in_reply_to_account_id": None,
            "sensitive": False,
            "spoiler_text": "",
            "visibility": "public",
            "language": "en",
            "uri": uri,
            "url": uri,
            "replies_count": 0,
            "reblogs_count": 0,
            "favourites_count": 0,
            "edited_at": None,
            "favourited": False,
            "reblogged": False,
            "muted": False,
            "bookmarked": False,
            "content": f"Timeline paused for {timeout} seconds",
            "filtered": [],
            "reblog": None,
            "account": {
                "id": "0",
                "username": "MentalProxy",
                "acct": "MentalProxy@local.local",
                "display_name": "Mental Proxy",
                "locked": False,
                "bot": True,
                "discoverable": True,
                "group": False,
                "created_at": "2023-01-15T00:00:00.000Z",
                "note": "Mental wellbeing features for social media websites",
                "url": "https://mentalproxy.sergia.ch",
                "avatar": None,
                "avatar_static": None,
                "header": None,
                "header_static": None,
                "followers_count": 1,
                "following_count": 1,
                "statuses_count": 1,
                "last_status_at": "2023-01-28",
                "emojis": [],
                "fields": [
                    {
                        "name": "Website/Blog",
                        "value": "<a href=\"https://mentalproxy.sergia.ch/\" rel=\"nofollow noopener noreferrer\" target=\"_blank\"><span class=\"invisible\">https://www.</span><span class=\"\">mentalproxy.sergia.ch/</span><span class=\"invisible\"></span></a>",
                        "verified_at": None
                    }
                ]
            },
            "media_attachments": [],
            "mentions": [],
            "tags": [
                # {
                #     "name": "morning",
                #     "url": "https://dair-community.social/tags/morning"
                # }
            ],
            "emojis": [],
            "card": None,
            "poll": None
        }
    
    def reduce_toot_count(self, response, limit=10):
        if not self.get_is_path_manytoots(profile_maxid_required=False):
            return
        assert isinstance(limit, int), limit
        data = response.content
        data = data.decode('utf-8')
        data = json.loads(data)
        data = data[:limit]
        data.append(self.insert_pause_toot())
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
            # self.send_error(403, f"Timeline paused for {} more seconds...")
            timeout = int(self.rate_limiter.notifications_remaining_time)
            self.send_json([self.insert_pause_toot(timeout)])
            
            # send an empty json (no error, shows as empty)
            # self.send_empty_json()
            return True
    
    def disable_scroll_events(self, response: Response):
        if 'application/javascript' != response.headers.get('content-type'):
            return
        
        data = response.content
        data = data.replace(b'this.attachScrollListener(),', b'')
        
        # disable websocket onclose
        data = data.replace(b'n.onclose=s,', b'')
        
        if data != response.content:
            print('JS Data Changed!')
        # else:
        #     print('JS file', self.path, 'NOT changed')
            
            # if b'attachScrollListener()' in response.content:
            #     # print(response.content)
            #     with open('a.txt', 'wb') as f:
            #         f.write(response.content)
            #     raise ValueError('FOUND')
        
        response._content = data
    
    def process_response(self, response):
        """Process the response from the destination."""
        super(BaseMastodonEthicalProxy, self).process_response(response)
        self.disable_websockets(response)
        self.reduce_toot_count(response)
        self.disable_scroll_events(response)