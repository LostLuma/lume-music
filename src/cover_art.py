import re

import aiohttp

# Escape regex copied from python-musicbrainzngs at
# https://github.com/alastair/python-musicbrainzngs
LUCENE_SPECIAL = r'([+\-&|!(){}\[\]\^"~*?:\\\/])'


async def find_cover_art(artist: str | None, album: str | None) -> str | None:
    if artist is None or album is None:
        return

    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Lume Music/1.0 (+https://github.com/LostLuma/lume-music)',
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        search: list[str] = [
            'artist:' + re.sub(LUCENE_SPECIAL, r'\\\1', artist),
            'release:' + re.sub(LUCENE_SPECIAL, r'\\\1', album),
        ]

        params: dict[str, str] = {
            'inc': 'various-artists',
            'query': ' AND '.join(search),
        }

        async with session.get('https://musicbrainz.org/ws/2/release', params=params) as resp:
            if not resp.ok:
                return

            data = await resp.json()

    for result in data.get('releases', []):
        id = result['id']
        return f'https://coverartarchive.org/release/{id}/front'
