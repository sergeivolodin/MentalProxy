from http.server import ThreadingHTTPServer
from argparse import ArgumentParser
from rate_limiter import RateLimiterPostsNotifications, RateLimiterAlwaysNo, RateLimiterAlwaysYes, RateLimiterPostsPerMinute
from twitter_ethical_proxy import BaseTwitterEthicalProxy

# argument parser
parser = ArgumentParser(description="Run a proxy for Twitter with mental wellbeing features")
parser.add_argument('--listen_port', type=str, help="Port to listen on, default is 8080", default=8080)

def run(listen_port):
    """Run the server."""
    server_address = ('', listen_port)
    ratelimiter = RateLimiterPostsNotifications()
    handler_class = BaseTwitterEthicalProxy\
        .with_limit(ratelimiter)
    httpd = ThreadingHTTPServer(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    args = parser.parse_args()
    print(f"Now open http://127.0.0.1:{args.listen_port} to access Twitter with mental wellbeing features")
    run(int(args.listen_port))