from twisted.internet import reactor
from twisted.web import proxy, server
from twisted.protocols.tls import TLSMemoryBIOFactory
from twisted.internet import ssl, defer, task, endpoints
from urllib.parse import quote as urlquote, urlparse, urlunparse

from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.web.http import _QUEUED_SENTINEL, HTTPChannel, HTTPClient, Request
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET


# https://stackoverflow.com/questions/35664007/python-twisted-reverse-proxy-to-https-api-could-not-connect

class HTTPSReverseProxyResource(proxy.ReverseProxyResource, object):
    def proxyClientFactoryClass(self, *args, **kwargs):
        """
        Make all connections using HTTPS.
        """
        return TLSMemoryBIOFactory(
            ssl.optionsForClientTLS(self.host.decode("ascii")), True,
            super(HTTPSReverseProxyResource, self)
            .proxyClientFactoryClass(*args, **kwargs))
    def getChild(self, path, request):
        """
        Ensure that implementation of C{proxyClientFactoryClass} is honored
        down the resource chain.
        """
        child = super(HTTPSReverseProxyResource, self).getChild(path, request)
        return HTTPSReverseProxyResource(child.host, child.port, child.path,
                                         child.reactor)

class EthicalProxy(HTTPSReverseProxyResource):
    def process(self):
        self.changeHeaders()
        return super(self).process(self)

    def getChild(self, path, request):
        child = super(EthicalProxy, self).getChild(path, request)
        return EthicalProxy(child.host, child.port, child.path,
                                         child.reactor)

    def changeHeaders(self):
        # Inject an extra request header.
        print(self.requestHeaders)
        self.requestHeaders.addRawHeader(b"Xzone", b"foo.com")
    def render(self, request):
        """
        Render a request by forwarding it to the proxied server.
        """
        print('render')
        # RFC 2616 tells us that we can omit the port if it's the default port,
        # but we have to provide it otherwise
        host = self.host
        request.requestHeaders.setRawHeaders(b"host", [host])
        request.content.seek(0, 0)
        qs = urlparse(request.uri)[4]
        if qs:
            rest = self.path + b"?" + qs
        else:
            rest = self.path
        clientFactory = self.proxyClientFactoryClass(
            request.method,
            rest,
            request.clientproto,
            request.getAllHeaders(),
            request.content.read(),
            request,
        )
        self.reactor.connectTCP(self.host, self.port, clientFactory)
        return NOT_DONE_YET


host = b'dair-community.social'

site = server.Site(EthicalProxy(host, 443, b''))
reactor.listenTCP(8082, site)
reactor.run()
