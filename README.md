## Mastodon Ethical Proxy

We want to create a proxy server for the Mastodon network, such that it can add mental wellbeing functionality

See https://dair-community.social/@sergia/109660753217484908

## How to run
`python proxy.py --instance <your_instance_name>`

### Proposed functionality:
- Queueing notifications https://github.com/mastodon/mastodon/issues/23015
- Delaying notifications https://github.com/mastodon/mastodon/issues/23015
- (later) Queueing posts
- Multiple and custom timelines
- Direct Sharing https://dair-community.social/@sergia/109513867125571339

### Plan
1. Check if a Python proxy server can work for Mastodon, as a web interface and on the phone app... Works with the web interface!
2. Check if basic data can be changed... Yes
3. Implement queued/delayed notifications

### Why a proxy?
- Backend changes are possible for Mastodon, but not for commercial social media
- Browser extensions are avilable for Desktop (Firefox, Chrome), but not for mobile (Firefox for Android slowly is getting there).
- It's not possible so far to use any method for apps whatsoever. For example, even the Mastodon app would have to be changed, unless the backend is changed

At the core, there's a conviction that a customer should be able to have control over the service they receive. Since the social media companies do not provide that, do not want to and will not do it, we do not ask them and do our own.

Proxy is an elegant solution that can support both open-source and commercial social media, and theoretically all of the clients.
For the Apps, we propose the following scheme: PAC file to route API requests for social media through the proxy. It is unclear yet if apps do certificate pinning. If they do, it's likely this would not work. A custom certificate would be required.

To account for trust/security with regard to the proxy, we propose to a) run self-hosted instances and b) deploy code from the master branch to a known service like Heroku, expose a read-only API key to be able to inspect how the container was created (TBD).

I'm looking at re-writing everything in JavaScript, so the same code can be used for a Browser Extension (TBD), the Reverse Proxy and the Forward Proxy (TBD)
