
from typing import Literal, TypedDict


class _AdditionalInfo(TypedDict):
    duration_ms: int
    submission_client: str
    submission_client_version: str


class _TrackMetadata(TypedDict):
    artist_name: str
    release_name: str
    track_name: str
    additional_info: _AdditionalInfo


class _Payload(TypedDict):
    track_metadata: _TrackMetadata


class Event(TypedDict):
    listen_type: Literal['playing_now']
    payload: list[_Payload]
