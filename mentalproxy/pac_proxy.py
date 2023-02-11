from mitm.core import Connection, Middleware, Protocol
from mitm import MITM, CertificateAuthority
from mitm import MITM, protocol, middleware, crypto
from typing import Tuple
from pathlib import Path

path = '/home/sergia/.mitm'
certificate_authority = CertificateAuthority.init(path=Path(path))

#class DomainRedirect(Middleware):
class DomainRedirect(protocol.HTTP):
    async def resolve(c: Connection, data: bytes) -> Tuple[str, int, bool]:
        return None
        print(c, data, 'saq')
        if data.startswith('CONNECT api.twitter.com:443'):
            return ('0.0.0.0', 443, True)
        host, port, is_encrypted = await super().resolve(c, data)
        return (host, port, is_encrypted)

mitm = MITM(
    host="0.0.0.0",
    port=8443,
    protocols=[DomainRedirect], 
    middlewares=[middleware.Log], # middleware.HTTPLog used for the example below.
    certificate_authority = certificate_authority
)
mitm.run()
