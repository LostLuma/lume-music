import asyncio
import time
from typing import Any, ClassVar, Literal, NotRequired, Optional, TypedDict

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
    userloved: NotRequired[bool]
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


def pad_or_slice(data: str | None) -> str | None:
    if data is None:
        return data

    # Rich Presence text fields are
    # Restricted within 2 to 32 characters
    if len(data) == 1:
        return data + '\u200b'
    elif len(data) > 32:
        return data[:30] + '..'

    return data


async def _update_presence(event: Event | None) -> None:
    now = time.time()

    if State.last_update == 0:
        await presence.connect()
    else:
        diff = now - State.last_update

        if (diff < 15):
            await asyncio.sleep(diff)

    State.last_update = time.time()

    if event is None:
        await presence.clear()
    else:
        elapsed: int = event['data']['song']['parsed']['currentTime'] or 0
        duration: int = event['data']['song']['processed']['duration'] or 0

        kwargs: dict[str, Any] = {
            'start': int(now - elapsed),
            'end': int(now + duration - elapsed),
            'state': pad_or_slice(event['data']['song']['processed']['artist']),
            'details': pad_or_slice(event['data']['song']['processed']['track']),
            'large_text': pad_or_slice(event['data']['song']['processed']['album']),
            'buttons': [
                {
                    'label': 'Listen Along!',
                    'url': event['data']['song']['parsed']['originUrl'],
                },
            ],
        }

        if event['data']['song']['metadata'].get('userloved'):
            kwargs['small_text'] = 'Loved'
            kwargs['small_image'] = 'https://files.lostluma.net/6KJOa4.png'

        if event['data']['song']['parsed']['trackArt'] is None:
            kwargs['large_image'] = 'https://files.lostluma.net/PoMvyI.gif'
        else:
            kwargs['large_image'] = event['data']['song']['parsed']['trackArt']

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
