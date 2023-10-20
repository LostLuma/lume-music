from typing import TypedDict


class _Button(TypedDict):
    url: str
    label: str


class UpdatePresence(TypedDict, total=False):
    state: str
    details: str
    start: int
    end: int
    large_image: str
    large_text: str
    small_image: str
    small_text: str
    party_id: str
    party_size: list  # pyright: ignore # pypresence type hints are so bad ...
    join: str
    spectate: str
    match: str
    buttons: list[_Button]
    instance: bool
