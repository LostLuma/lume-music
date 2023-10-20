import asyncio
import time
from typing import ClassVar, Optional, Unpack

import pypresence  # pyright: ignore[reportMissingTypeStubs]

from .types.pypresence import UpdatePresence

# Lume Music!
CLIENT_ID = '918549563487432734'


class Presence:
    _last_update: ClassVar[float] = 0
    _update_task: ClassVar[Optional[asyncio.Task[None]]] = None

    _presence: ClassVar[pypresence.AioPresence] = pypresence.AioPresence(client_id=CLIENT_ID)

    @staticmethod
    def update(**kwargs: Unpack[UpdatePresence]) -> None:
        if Presence._update_task is not None:
            Presence._update_task.cancel()

        Presence._update_task = asyncio.create_task(Presence._update(**kwargs))

    @staticmethod
    async def _update(**kwargs: Unpack[UpdatePresence]) -> None:
        now = time.time()

        if Presence._last_update == 0:
            await Presence._presence.connect()
        else:
            diff = now - Presence._last_update

            if (diff < 15):
                await asyncio.sleep(diff)

        Presence._last_update = time.time()

        if not kwargs:
            await Presence._presence.clear()
        else:
            try:
                await Presence._presence.update(**kwargs)  # pyright: ignore[reportUnknownMemberType]
            except pypresence.PipeClosed:
                await Presence._presence.connect()
                await Presence._presence.update(**kwargs)  # pyright: ignore[reportUnknownMemberType]

            try:
                start = kwargs['start']
                end = kwargs['end']
            except KeyError:
                return  # No duration set

            await asyncio.sleep(end - start + 5)
            await Presence._presence.clear()  # Cancelled if a new song is playing
