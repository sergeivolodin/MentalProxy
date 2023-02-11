from mitmproxy import http
from mitmproxy import ctx
import re

def request(flow: http.HTTPFlow) -> None:
    url = flow.request.url
    host = flow.request.host
    if flow.request.host == 'api.twitter.com':
        start = 'https://api.twitter.com/'
        flow.request.host = '127.0.0.1:8086'
        flow.request.url = 'http://127.0.0.1:8086/__proxy_prefix_https%3A%2F%2Fapi.twitter.com/' + url[len(start):]
    if flow.request.url.startswith('https://twitter.com/'):
        start = 'https://twitter.com/'
        flow.request.host = '127.0.0.1:8086'
        flow.request.url = 'http://127.0.0.1:8086/' + url[len(start):]
    print(url, host, flow.request.host, flow.request.url)
