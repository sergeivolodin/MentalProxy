from http.server import BaseHTTPRequestHandler
import requests
import re
from urllib.parse import urlparse, unquote
from urllib.parse import parse_qs
from mentalproxy.helpers import remove_cookie_word


class BaseReverseProxyHandler(BaseHTTPRequestHandler):
    """Reverse Proxy Server class."""
    
    @classmethod
    def point_to(cls, destination_schema, destination_host):
        """Create a class that has a specific host/port."""
        
        class ReverseProxyHandler(cls):
            @property
            def destination_schema(self):
                return destination_schema
            
            @property
            def destination_host(self):
                return destination_host

        return ReverseProxyHandler
    
    @property
    def destination_schema(self):
        """Destination schema (to be overloaded)."""
        raise NotImplementedError
    
    @property
    def destination_host(self):
        """Destination host (to be overloaded)."""
        raise NotImplementedError
    
    # def override_dst_host(self, newHost):
    #     self.newDstHost = newHost
        
    # def get_dst_host(self):
    #     if hasattr(self, 'newDstHost') and self.newDstHost:
    #         return self.newDstHost
    #     return self.destination_host
        
    # def reset_dst_host(self):
    #     self.newDstHost = None
    
    @property
    def destination_host_from_url(self):
        url = self.destination_url
        url = urlparse(url)
                
        if url.hostname is None:
            return self.destination_host
        else:
            return url.hostname
    
    def get_proxy_headers(self):
        """Get the headers to be sent to the destination."""
        headers = {x.lower(): y for x, y in self.headers.items()}
        self.headers_lowercase = dict(headers)
        headers['host'] = self.destination_host_from_url
        headers['origin'] = self.destination_base_url
        headers['referer'] = self.destination_base_url
        return headers
    
    @property
    def destination_base_url(self):
        """Get the base URL for the destination."""
        return self.destination_schema + '://' + self.destination_host
    
    @property
    def destination_url(self):
        """Get destination URL based on request URL."""
        url = self.destination_base_url + self.path        
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        if '__proxy_url' in query_params:
            target_url = query_params['__proxy_url'][0]
            return target_url
        
        if '__proxy_prefix' in self.path:
            url1 = self.path.split('/')
            prefix = unquote(url1[1][len('__proxy_prefix_'):])
            postfix = '/'.join(url1[2:])
            return prefix + '/' + postfix
                
        return url
    
    def send_response(self, code, message=None):
        """Overloading send_response to not send our server&date."""
        self.log_request(code)
        self.send_response_only(code, message)
    
    @property
    def delete_response_headers(self):
        return ['content-encoding', 'transfer-encoding', 'connection', 'vary', 'content-security-policy']
    
    def remove_cookie_secure_attribute(self, cookie):
        """Remove the secure parameter from set-cookie headers."""
        return remove_cookie_word(cookie, 'secure')
    
    def process_cookies(self, method, headers):
        if 'set-cookie' not in headers:
            return
        if isinstance(headers['set-cookie'], str):
            headers['set-cookie'] = method(headers['set-cookie'])
        if isinstance(headers['set-cookie'], list):
            for i, item in enumerate(headers['set-cookie']):
                headers['set-cookie'][i] = method(item)
    
    def process_cookies_from_server(self, headers):
        self.process_cookies(self.remove_cookie_secure_attribute, headers)
    
    def send_proxied_headers(self, response):
        """Post-process and relay the headers from the destination."""
        response_headers = {x.lower(): y for x, y in response.headers.items()}
        
        for item in self.delete_response_headers:
            if item in response_headers:
                del response_headers[item]
                
        response_headers['content-length'] = len(response.content)
        if 'set-cookie' in response_headers:
            response_headers['set-cookie'] = response.raw.headers.getlist('set-cookie')
        
        self.process_cookies_from_server(response_headers)
        
        for x, y in response_headers.items():
            if isinstance(y, str):
                self.send_header(x, y)
            if isinstance(y, list):
                for ysub in y:
                    self.send_header(x, ysub)
        self.end_headers()
        
    def ignore_integrity(self, response, name='integrity'):
        """Remove the integrity checks for assets."""
        if 'text/html' not in response.headers.get('content-type', ''):
            return
        regexp = re.compile(name.encode('utf-8') + b'="[^"]+"')
        response._content = re.sub(regexp, b"", response.content)
        
    def process_response(self, response):
        """Process the response from the destination."""
        response.headers = {x.lower(): y for x, y in response.headers.items()}
        self.ignore_integrity(response)
        pass
        
    def send_proxied_response(self, response):
        """Send the response from the destination to the client."""
        self.process_response(response)
        self.send_response(response.status_code)
        self.send_proxied_headers(response)   
             
        self.wfile.write(response.content)
        
    def filter_incoming_request(self):
        """Reject certain incoming requests."""
        pass
    
    def get_header(self, header):
        """Get the header in the request, case-insensitive."""
        for x, y in self.headers.items():
            if x.lower() == header.lower():
                return y
        return None
        
    def process_no_data(self):
        """Process a request assuming there was no data sent."""
        if self.filter_incoming_request():
            return
        response = requests.request(
            method=self.command,
            url=self.destination_url,
            headers=self.get_proxy_headers()
        )
                
        self.send_proxied_response(response)
    
    def process_with_data(self):
        """Process a request assuming there was data"""
        if self.filter_incoming_request():
            return
        post_length = int(self.get_header('content-length'))
        response = requests.request(
            method=self.command,
            url=self.destination_url,
            headers=self.get_proxy_headers(),
            data=self.rfile.read(post_length)
        )
        self.send_proxied_response(response)
        
    def process(self):
        if self.get_header('content-length'):
            self.process_with_data()
        else:
            self.process_no_data()
            
    def do_GET(self):
        self.process()
        
    def do_DELETE(self):
        self.process()
        
    def do_POST(self):
        self.process()
        
    def do_PATCH(self):
        self.process()
        
    def do_HEAD(self):
        self.process()
        
    def do_PUT(self):
        self.process()

    def do_OPTIONS(self):
        self.process()
