from typing import List


class PACWriter:
    """Write Proxy Auto-Configuration Files."""
    
    # for examples, see https://docs.thousandeyes.com/product-documentation/global-vantage-points/enterprise-agents/proxy/writing-and-testing-proxy-auto-configuration-pac-files    
    
    def __init__(self):
        pass
    
    def body(self):
        raise NotImplementedError
    
    def generate(self):
        s = "function FindProxyForURL(url, host)\n{\n"
        s += self.body()
        s += "\n}"
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
        s = f'if (dnsDomainIs(host, "{host}"))'
        s += '\n{\n'
        s += f'  return "PROXY {proxy}";'
        s += '\n}'
        return s
        
    def body(self):
        s = ""
        for e in self.exceptions:
            s += self.exceptionStatement(e, self.proxy)
            s += '\n'
        s += DirectPACWriter.returnDirect()
        return s
    