from http.server import BaseHTTPRequestHandler
import requests
import re


class BaseReverseProxyHandler(BaseHTTPRequestHandler):
    """Reverse Proxy Server class."""
    
    def factory(destination_schema, destination_host):
        """Create a class that has a specific host/port."""
        
        class ReverseProxyHandler(BaseReverseProxyHandler):
            def get_destination_schema(self):
                return destination_schema
            def get_destination_host(self):
                return destination_host

        return ReverseProxyHandler
    
    def get_destination_schema(self):
        """Destination schema (to be overloaded)."""
        raise NotImplementedError
    
    def get_destination_host(self):
        """Destination host (to be overloaded)."""
        raise NotImplementedError
    
    def get_proxy_headers(self):
        """Get the headers to be sent to the destination."""
        headers = {x.lower(): y for x, y in self.headers.items()}
        headers['host'] = self.get_destination_host()
        headers['origin'] = self.get_destination_base_url()
        headers['referer'] = self.get_destination_base_url()
        return headers
    
    def get_destination_base_url(self):
        """Get the base URL for the destination."""
        return self.get_destination_schema() + '://' + self.get_destination_host()
    
    def get_destination_url(self):
        """Get destination URL based on request URL."""
        return self.get_destination_base_url() + self.path
    
    def send_response(self, code, message=None):
        """Overloading send_response to not send our server&date."""
        self.log_request(code)
        self.send_response_only(code, message)
    
    def send_proxied_headers(self, response):
        """Post-process and relay the headers from the destination."""
        response_headers = {x.lower(): y for x, y in response.headers.items()}
        for item in ['content-encoding', 'transfer-encoding', 'connection', 'vary', 'content-security-policy']:
            if item in response_headers:
                del response_headers[item]
        response_headers['content-length'] = len(response.content)
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
        
    def do_GET(self):
        self.filter_incoming_request()
        response = requests.get(
            self.get_destination_url(),
            headers=self.get_proxy_headers()
        )
        self.send_proxied_response(response)
    
    def do_POST(self):
        post_length = int(self.get_header('content-length'))
        response = requests.post(
            self.get_destination_url(),
            headers=self.get_proxy_headers(),
            data=self.rfile.read(post_length)
        )
        self.send_proxied_response(response)