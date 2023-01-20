from http.server import ThreadingHTTPServer
from argparse import ArgumentParser
from rate_limiter import RateLimiterAlwaysNo, RateLimiterAlwaysYes, RateLimiterPostsPerMinute
from mastodon_ethical_proxy import BaseMastodonEthicalProxy

# argument parser
parser = ArgumentParser(description="Run a proxy for Mastodon with mental wellbeing features")
parser.add_argument('--instance', type=str, help="Host name, example: mastodon.social", required=True)
parser.add_argument('--listen_port', type=str, help="Port to listen on, default is 8080", default=8080)

# configuration
destination_schema = 'https'

def run(listen_port, destination_host):
    """Run the server."""
    server_address = ('', listen_port)
    ratelimiter = RateLimiterAlwaysNo()
    handler_class = BaseMastodonEthicalProxy\
        .point_to(destination_schema, destination_host)\
        .with_limit(ratelimiter)
    httpd = ThreadingHTTPServer(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    args = parser.parse_args()
    print(f"Now open http://127.0.0.1:{args.listen_port} to access {args.instance} with mental wellbeing features")
    run(int(args.listen_port), args.instance)