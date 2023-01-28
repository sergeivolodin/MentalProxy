from http.server import ThreadingHTTPServer
from argparse import ArgumentParser
from .rate_limiter import RateLimiterPostsNotifications, RateLimiterAlwaysNo, RateLimiterAlwaysYes, RateLimiterPostsPerMinute
from .mastodon_ethical_proxy import BaseMastodonEthicalProxy
import multiprocessing
from .helpers import find_free_port, waitOnline
import pytest
import requests
from time import sleep


TEST_INSTANCE = 'dair-community.social'
PORT = find_free_port()

def create_local_proxy(port, run=False):
    server_address = ('', port)
    ratelimiter = RateLimiterPostsNotifications()
    handler_class = BaseMastodonEthicalProxy.setGlobal(
        destination_schema='https',
        destination_host=TEST_INSTANCE,
        rate_limiter=ratelimiter)
    httpd = ThreadingHTTPServer(server_address, handler_class)
    if run:
        httpd.serve_forever()
    return httpd

@pytest.fixture(autouse=True)
def free_port():
    port = find_free_port()
    yield port
    pass

@pytest.fixture()
def start_server(free_port):
    p = multiprocessing.Process(target=create_local_proxy, args=(free_port,), kwargs={'run': True})
    p.start()
    waitOnline(free_port)
    yield
    p.terminate()


def test_can_create_server(free_port):
    httpd = create_local_proxy(free_port)
    assert httpd
    del httpd
    
def test_can_get_homepage(start_server, free_port):
    resp = requests.get(f'http://localhost:{free_port}')
    assert resp.ok
    assert 'Mastodon' in resp.text