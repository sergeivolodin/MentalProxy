import socket
from contextlib import closing
import requests
from time import sleep, time
from threading import Lock
from uuid import uuid4


class WithGlobals(object):
    """Set the attribute for a class"""

    @classmethod
    def __setglobals__(cls):
        pass

    @classmethod
    def setGlobal(cls, **kwargs):
        kwargs = dict(kwargs)
        
        for key in kwargs.keys():
            assert isinstance(key, str)
            assert hasattr(cls, key), (cls, key)
            
        assert not hasattr(cls, 'withGlobalsListGlobals')
        kwargsOrig = dict(kwargs)
        def withGlobalsListGlobals(cls):
            return kwargsOrig
        
        kwargs['withGlobalsListGlobals'] = classmethod(withGlobalsListGlobals)
            
        newName = cls.__name__ + '_' + str(uuid4())
        NewClass = type(newName, (cls,), kwargs)
        NewClass.__setglobals__()
            
        return NewClass

class IDIncreaser():
    """Return increasing ids, thread-safe."""
    def __init__(self):
        self.id_ = 10000
        self.lock = Lock()
        
    def getId(self):
        with self.lock:
            id_ = self.id_
            self.id_ -= 1
        return id_


def find_free_port():
    """Find a free port in the system."""
    
    # from https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
    
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def waitOnline(port, host='localhost', schema='http', delay=0.1, timeout=3):
    """Wait until the server is online."""
    tstart = time()
    while True:
        tnow = time()
        tdelta = tnow - tstart
        if tdelta >= timeout:
            raise ValueError(f"Server {schema}://{host}:{port} is offline for {timeout} seconds")
        
        try:
            resp = requests.get(f'{schema}://{host}:{port}')
            if resp.ok:
                return
        except requests.exceptions.ConnectionError:
            pass
        sleep(delay)
        
        
def remove_cookie_word(cookies: str, word: str) -> str:    
    def getkey(cookie):
        if len(cookie.split('=')) != 2:
            return None
        return cookie.split('=')[0]
    
    # removing key-values like Domain=...
    
    def filter_word(cookie):
        if cookie.lower() == word.lower():
            return False
        if getkey(cookie) and getkey(cookie).lower() == word.lower():
            return False
        return True
    
    cs = cookies.split(';')
    cs = [c.split(',') for c in cs]
    cs = [[x.strip() for x in c] for c in cs]
    cs = [[x for x in c if filter_word(x)] for c in cs]
    
    cs = [', '.join(c) for c in cs if c]
    cs = '; '.join(cs)
    return cs
