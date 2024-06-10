from typing import Optional
from pydantic import BaseModel

class SimpleLyrics(BaseModel):
    plain_lyrics: Optional[str]
    synced_lyrics: Optional[str]
    instrumental: bool = False

class SimpleTrack(BaseModel):
    id: int
    name: str
    artist_name: str
    album_name: str
    duration: int
    last_lyrics: Optional[SimpleLyrics]