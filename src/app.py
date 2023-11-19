import time

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response

from .cover_art import find_cover_art
from .presence import Presence
from .types.listenbrainz import Event as ListenBrainzEvent
from .types.pypresence import UpdatePresence
from .types.web_scrobbler import Event as WebScrobblerEvent
from .utils import pad_or_slice

app = Starlette()


LOVED_ICON = 'https://files.lostluma.net/6KJOa4.png'
ALBUM_ICON = 'https://files.lostluma.net/PoMvyI.gif'


@app.route('/event/web-scrobbler', methods=['POST'])  # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
async def on_web_scrobbler_event(request: Request) -> Response:
    event: WebScrobblerEvent = await request.json()

    if event['eventName'] == 'paused':
        Presence.update()
    elif event['eventName'] in ['nowplaying', 'resumedplaying']:
        now = time.time()
        song = event['data']['song']

        elapsed: int = song['parsed']['currentTime'] or 0
        duration: int = song['processed']['duration'] or 0

        kwargs: UpdatePresence = {
            'start': int(now - elapsed),
            'end': int(now + duration - elapsed),
            'buttons': [
                {
                    'label': 'Listen Along!',
                    'url': song['parsed']['originUrl'],
                },
            ],
        }

        track = song['processed']['track']
        album = song['processed']['album']
        artist = song['processed']['artist']

        if track is not None:
            kwargs['details'] = pad_or_slice(track)

        if album is not None:
            kwargs['large_text'] = pad_or_slice(album)

        if artist is not None:
            kwargs['state'] = pad_or_slice(artist)

        if song['metadata'].get('userloved'):
            kwargs['small_text'] = 'Loved'
            kwargs['small_image'] = LOVED_ICON

        track_art = song['parsed']['trackArt']

        if track_art is not None:
            kwargs['large_image'] = track_art
        else:
            url = await find_cover_art(artist, album)
            kwargs['large_image'] = url or ALBUM_ICON  # Always set an image so the loved icon shows properly

        Presence.update(**kwargs)

    return PlainTextResponse()


@app.route('/event/web-scrobbler', methods=['OPTIONS'])  # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
async def on_web_scrobbler_options(request: Request) -> Response:
    return Response(headers={'Access-Control-Allow-Origin': '*'})


# Allow adding the custom ListenBrainz server
@app.route('/event/listenbrainz/1/validate-token', methods=['GET'])  # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
async def on_pano_scrobbler_validate_token(request: Request) -> Response:
    data = {
        'code': 200,
        'valid': True,
        'message': 'Token valid.',
        'user_name': 'Lume Music',
    }

    return JSONResponse(data)


# TODO: Maybe fetch whether the user loved the track via last.fm API
@app.route('/event/listenbrainz/1/submit-listens', methods=['POST'])  # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
async def on_pano_scrobbler_submit_listens(request: Request) -> Response:
    event: ListenBrainzEvent = await request.json()

    if event['listen_type'] == 'playing_now' and event['payload']:
        now = int(time.time())
        song = event['payload'][0]['track_metadata']

        track = song['track_name']
        album = song['release_name']
        artist = song['artist_name']
        duration = int(song['additional_info']['duration_ms'] / 1000)

        kwargs: UpdatePresence = {
            'start': now,
            'end': now + duration,
            'state': pad_or_slice(artist),
            'details': pad_or_slice(track),
            'large_text': pad_or_slice(album),
        }

        url = await find_cover_art(artist, album)
        kwargs['large_image'] = url or ALBUM_ICON

        Presence.update(**kwargs)

    return JSONResponse({'status': 'ok'})
