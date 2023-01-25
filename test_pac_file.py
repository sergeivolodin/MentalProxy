from .pac_file import DirectWithExceptionsPACWriter, DirectPACWriter
        
def test_direct_with_exceptions():
    import pypac
    proxy = 'abacaba.com:8080'
    proxys = f'PROXY {proxy}'
    exceptions = ['twitter.com', 'mastodon.social']
    
    pac_file = DirectWithExceptionsPACWriter(proxy, exceptions).generate()
    parsed = pypac.get_pac(js=pac_file)
    found = parsed.find_proxy_for_url('https://mastodon.social', 'mastodon.social')
    assert found == proxys
    
    found = parsed.find_proxy_for_url('http://mastodon.social', 'mastodon.social')
    assert found == proxys
    
    found = parsed.find_proxy_for_url('http://twitter.com', 'twitter.com')
    assert found == proxys
    
    found = parsed.find_proxy_for_url('http://mastodon123.social', 'mastodon123.social')
    assert found == 'DIRECT'

def test_direct():
    import pypac
    pac_file = DirectPACWriter().generate()
    
    parsed = pypac.get_pac(js=pac_file)
    
    found = parsed.find_proxy_for_url('https://mastodon.social', 'mastodon.social')
    assert found == 'DIRECT'