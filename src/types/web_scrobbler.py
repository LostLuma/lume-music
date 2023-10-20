
from typing import Literal, NotRequired, TypedDict


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
    eventName: Literal['nowplaying', 'paused']
    data: _Data
