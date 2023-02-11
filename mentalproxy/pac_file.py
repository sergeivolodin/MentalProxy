from typing import List


class PACWriter:
    """Write Proxy Auto-Configuration Files."""
    
    # for examples, see https://docs.thousandeyes.com/product-documentation/global-vantage-points/enterprise-agents/proxy/writing-and-testing-proxy-auto-configuration-pac-files    
    
    def __init__(self):
        pass
    
    def body(self):
        raise NotImplementedError
    
    def generate(self):
        def indent(text, count=2):
            return '\n'.join([' ' * count + x for x in text.split('\n')])
        s = "function FindProxyForURL(url, host) {\n"
        s += indent(self.body())
        s += "\n}\n"
        return s
    
    @classmethod
    def download_metadata(cls):
        return {
            'mime': 'application/x-ns-proxy-autoconfig',
            'extension': 'pac'
        }
        
class DirectPACWriter(PACWriter):
    """PAC without any proxy."""
    
    @classmethod
    def returnDirect(cls):
        return 'return "DIRECT";'
    
    def body(self):
        return DirectPACWriter.returnDirect()
    

class DirectWithExceptionsPACWriter(PACWriter):
    """Exceptions go through a proxy, the rest goes through directly."""
    
    def __init__(self, proxy: str, exceptions: List[str]):
        
        assert isinstance(proxy, str), proxy
        assert isinstance(exceptions, list), exceptions
        assert all([isinstance(t, str) for t in exceptions]), exceptions
        
        self.proxy = proxy
        self.exceptions = exceptions
        
    def exceptionStatement(self, host, proxy):
        if host[0].isalpha():
            s  = f'if (dnsDomainIs(host, "{host}") || shExpMatch(url, "*{host}*"))' + '\n'
        else:
            s  = f'if (shExpMatch(host, "{host}") || shExpMatch(url, "{host}"))' + '\n'
        s += f'  return "PROXY {proxy}";\n'
        #s +=  ''
        return s
        
    def body(self):
        s = ""
        for e in self.exceptions:
            s += self.exceptionStatement(e, self.proxy)
            s += '\n'
        s += DirectPACWriter.returnDirect()
        return s
    

if __name__ == '__main__':
    fn = 'test_proxy'
    #proxy_address = 'proxy.mentalproxy.sergia.ch'
    proxy_address = '95.179.214.45' #'dev.walrus-liberty.ts.net'
    proxy_port = '8080'
    hostmap = ['dair-community.social', 'twitter.com', 'mobile.twitter.com', 'api.twitter.com', '178.33.220.142', '104.244.4*', '69.195.1*', ]
    hostmap = sorted(set(hostmap))
    data = DirectWithExceptionsPACWriter(proxy=f'{proxy_address}:{proxy_port}', exceptions=hostmap).generate()
    fn += '.' + DirectWithExceptionsPACWriter.download_metadata()['extension']
    with open('www/' + fn, 'w') as f:
        f.write(data)
