import socket
from contextlib import closing
import requests
from time import sleep, time


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