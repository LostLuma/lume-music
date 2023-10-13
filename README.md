Lume Music
==========

A small Python program to display your music from [web scrobbler](https://github.com/web-scrobbler/web-scrobbler) as your Discord status.

Installation
------------

- Install requirements via `pip install -Ur requirements.txt`
- Set up `python -m uvicorn --port 7950 main:app` to run as a permanent service
- Add `http://localhost:7950/event` as a webhook in the accounts section in web scrobbler
