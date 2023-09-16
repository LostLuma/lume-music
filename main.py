import asyncio
import time
from typing import Any, ClassVar, Literal, Optional, TypedDict

import pypresence  # pyright: ignore[reportMissingTypeStubs]
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

app = Starlette()
presence = pypresence.AioPresence(client_id='918549563487432734')


class State:
    last_update: ClassVar[float] = 0
    update_task: ClassVar[Optional[asyncio.Task[None]]] = None


class Song(TypedDict):
    track: str | None
    artist: str | None
    albumArtist: str | None
    album: str | None
    duration: int | None


class Parsed(Song):
    uniqueID: str | None
    currentTime: int | None
    isPlaying: bool
    trackArt: str | None
    isPodcast: bool
    originUrl: str


class RegexEdit(TypedDict):
    track: bool
    artist: bool
    album: bool
    albumArtist: bool


class Flags(TypedDict):
    isScrobbled: bool
    isCorrectedByUser: bool
    isRegexEditedByUser: RegexEdit
    isAlbumFetched: bool
    isValid: bool
    isMarkedAsPlaying: bool
    isSkipped: bool
    isReplaying: bool


class Metadata(TypedDict):
    userloved: bool
    startTimestamp: int
    label: str


class _Song(TypedDict):
    parsed: Parsed
    processed: Song
    noRegex: Song
    flags: Flags
    metadata: Metadata
    connectorLabel: str
    controllerTabId: int


class _Data(TypedDict):
    song: _Song


class Event(TypedDict):
    eventName: Literal["nowplaying", "paused"]
    data: _Data


def pad(data: str | None) -> str | None:
    if data is None or len(data) > 1:
        return data

    return data + '\u200b'


async def _update_presence(event: Event | None) -> None:
    if State.last_update == 0:
        await presence.connect()
    else:
        diff = time.perf_counter() - State.last_update

        if (diff < 15):
            await asyncio.sleep(diff)

    State.last_update = time.perf_counter()

    if event is None:
        await presence.clear()
    else:
        now = time.time()

        elapsed: int = event['data']['song']['parsed']['currentTime'] or 0
        duration: int = event['data']['song']['processed']['duration'] or 0

        kwargs: dict[str, Any] = {
            'state': pad(event['data']['song']['processed']['artist']),
            'details': pad(event['data']['song']['processed']['track']),
            'start': now - elapsed,
            'end': now + duration - elapsed,
            'large_image': event['data']['song']['parsed']['trackArt'],
            'large_text': pad(event['data']['song']['processed']['album']),
            'buttons': [
                {
                    'label': 'Listen Along!',
                    'url': event['data']['song']['parsed']['originUrl'],
                },
            ],
        }

        if event['data']['song']['metadata']['userloved']:
            kwargs['small_text'] = 'Loved'
            kwargs['small_image'] = 'https://files.lostluma.net/6KJOa4.png'

        try:
            await presence.update(**kwargs)  # pyright: ignore[reportUnknownMemberType]
        except pypresence.PipeClosed:
            await presence.connect()
            await presence.update(**kwargs)  # pyright: ignore[reportUnknownMemberType]

        if duration == 0:
            return

        # This is cancelled if another song is played
        await asyncio.sleep(duration + 5)
        await presence.clear()


def update_presence(event: Event | None) -> None:
    if State.update_task is not None:
        State.update_task.cancel()

    State.update_task = asyncio.create_task(_update_presence(event))


@app.route('/event', methods=['POST'])  # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
async def on_event(request: Request) -> Response:
    event: Event = await request.json()

    if event['eventName'] == 'paused':
        update_presence(None)
    elif event['eventName'] in ['nowplaying', 'resumedplaying']:
        update_presence(event)

    return PlainTextResponse()
