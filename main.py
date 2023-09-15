import asyncio
import time
from typing import Optional

import pypresence
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

app = Starlette()

last_update = 0
update_task: Optional[asyncio.Task[None]] = None

presence = pypresence.AioPresence(client_id='918549563487432734')


def pad(data: str) -> str:
    if len(data) > 1:
        return data
    return data + '\u200b'


@app.on_event('shutdown')
async def on_startup() -> None:
    presence.close()


async def _update_presence(**updates) -> None:
    global last_update

    if last_update == 0:
        await presence.connect()
    else:
        diff = time.perf_counter() - last_update

        if (diff < 15):
            await asyncio.sleep(diff)

    last_update = time.perf_counter()

    if not updates:
        await presence.clear()
    else:
        try:
            await presence.update(**updates)
        except pypresence.PipeClosed:
            await presence.connect()
            await presence.update(**updates)


def update_presence(**updates) -> None:
    global update_task

    if update_task is not None:
        update_task.cancel()

    update_task = asyncio.create_task(_update_presence(**updates))


@app.route('/event', methods=['POST'])
async def on_event(request: Request) -> Response:
    json = await request.json()

    data = json['data']
    event = json['eventName']

    parsed = data['song']['parsed']
    processed = data['song']['processed']
    metadata = data['song']['metadata']

    if event == 'paused':
        update_presence()
    elif event in ['nowplaying', 'resumedplaying']:
        update_presence(
            state=pad(processed['artist']),
            details=pad(processed['track']),
            start=metadata['startTimestamp'],
            end=metadata['startTimestamp'] + processed.get('duration', 0),
            large_image=parsed['trackArt'],
            large_text=pad(processed['album']),
            buttons=[
                {
                    "label": "Listen Along",
                    "url": parsed['originUrl'],
                },
            ],
        )

    return PlainTextResponse()
