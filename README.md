Lume Music
==========

A small Python program to display your music from [web scrobbler](https://github.com/web-scrobbler/web-scrobbler) as your Discord status.

Installation
------------

- Install requirements via `pip install -Ur requirements.txt`
- Set up `python -m uvicorn --port 7950 src:app` to run as a permanent service
- Add `http://localhost:7950/event/web-scrobbler` as a webhook in the accounts section in web scrobbler

Further Information
-------------------

Optionally, Lume Music can also receive events as a custom ListenBrainz server.  
This is most useful when listening to music on a mobile device using e.g. [Pano Scrobbler](https://play.google.com/store/apps/details?id=com.arn.scrobble).

Setting this up is a bit more complicated as Pano Scrobbler (or Android?) requires the API to be served with TLS.  
Another issue you may run into is that your devices are not always on the same network, but still need to communicate.

The solution I personally employ uses [tailscale](https://tailscale.com), as it just so happens to provide all the features we need:
- Your devices can communicate via a peer-to-peer network, even behind NAT
- Can provision a TLS certificate from Let's Encrypt for your device(s)
- And finally, it can use this certificate and act as a reverse proxy to funnel traffic to Lume Music

If you'd like to use this feel free to follow these steps:

- Install tailscale on both your computer and mobile device
- Serve the Lume Music API on your tailnet: ``tailscale serve --bg --https 7950 http://localhost:7950``
- Look up the URL under which the API is served via `tailscale serve status`
  - This should look something like `https://violet.beaver-beaver.ts.net:7950 (tailnet only)`
- Add a custom ListenBrainz server in the app using this URL
  - You will need to append `/event/listenbrainz` to the URL and provide a non-empty secret ([example here](https://files.lostluma.net/GTD7J4.png))

If you have more questions about the way tailscale works feel free to consult their documentation!
