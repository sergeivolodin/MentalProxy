from http.server import BaseHTTPRequestHandler
import requests
import re


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
    
    def get_proxy_headers(self):
        """Get the headers to be sent to the destination."""
        headers = {x.lower(): y for x, y in self.headers.items()}
        headers['host'] = self.destination_host
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
        return self.destination_base_url + self.path
    
    def send_response(self, code, message=None):
        """Overloading send_response to not send our server&date."""
        self.log_request(code)
        self.send_response_only(code, message)
    
    @property
    def delete_response_headers(self):
        return ['content-encoding', 'transfer-encoding', 'connection', 'vary', 'content-security-policy']
    
    def remove_cookie_security(self, response_headers):
        """Remove the secure parameter from set-cookie headers."""
        if 'set-cookie' in response_headers:
            if response_headers['set-cookie'].endswith('; secure'):
                response_headers['set-cookie'] = response_headers['set-cookie'][:-8]
    
    def send_proxied_headers(self, response):
        """Post-process and relay the headers from the destination."""
        response_headers = {x.lower(): y for x, y in response.headers.items()}
        
        for item in self.delete_response_headers:
            if item in response_headers:
                del response_headers[item]
                
        response_headers['content-length'] = len(response.content)
        
        self.remove_cookie_security(response_headers)
        
        for x, y in response_headers.items():
            self.send_header(x, y)
        self.end_headers()
        
    def ignore_integrity(self, response):
        """Remove the integrity checks for assets."""
        if 'text/html' not in response.headers.get('content-type', ''):
            return
        regexp = re.compile(b'integrity="[^"]+"')
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