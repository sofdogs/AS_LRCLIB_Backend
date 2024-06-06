from fastapi import FastAPI, HTTPException, Depends, Query
import asyncpg
from typing import List, Optional, Annotated
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# load the .env file
load_dotenv()

# create app
app = FastAPI()

# load database url 
DATABASE_URL = os.getenv("DATABASE_URL")

# to deploy 
origins = [
    "http://localhost:3000",
    "localhost:3000",
    "http://192.168.86.157:3000"
]

# enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# preprocessing the string by striping
# whitespace and converting to lowercase
def prepare_str(s: str): 
    return s.strip().lower()

# preprocessing the optional strings 
def prepare_optional_string(s: Optional[str]) -> Optional[str]:
    if s is None: 
        return None
    processed_val = prepare_str(s)
    if not processed_val: 
        return None
    return processed_val

# Dependency
async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# root connection
@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to LyricDB."}

# to check db connection 
@app.get("/health", response_model = dict)
async def health_check (db: asyncpg.Connection = Depends(get_db)):
    try:
        query = "SELECT 1"
        result = await db.fetchval(query)
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# uses id to get track info 
@app.get('/get/{id}', response_model = dict)
async def get_info(id: int, db: asyncpg.Connection = Depends(get_db)):
    query = """
    SELECT 
        t.id, 
        t.name, 
        t.artist_name, 
        t.album_name, 
        t.duration, 
        l.instrumental,
        l.plain_lyrics, 
        l.synced_lyrics
    FROM tracks t
    JOIN lyrics l on t.last_lyrics_id= l.id
    WHERE t.id = $1
    """
    row = await db.fetchrow(query, id)
    if not row: 
        raise HTTPException(status_code=404, detail="Track not found")
    return dict(row)

@app.get("/get/{artist_name}/{track_name}/{album_name}/{duration}",response_model = dict)
async def read_track(artist_name: str, track_name: str, album_name: str, duration: int, db: asyncpg.Connection = Depends(get_db)):
    # to lowercase 
    artist_name = artist_name.lower()
    track_name = track_name.lower()
    album_name = album_name.lower()

    query = """
    SELECT 
        t.id, 
        t.name, 
        t.artist_name, 
        t.album_name, 
        t.duration, 
        l.instrumental,
        l.plain_lyrics, 
        l.synced_lyrics
    FROM tracks t
    JOIN lyrics l on t.last_lyrics_id = l.id
    WHERE 
        artist_name_lower =  $1 AND 
        name_lower = $2 AND  
        album_name_lower = $3 AND 
        duration = $4
    ORDER BY
        tracks.id
    """
    row = await db.fetchrow(query, artist_name, track_name, album_name, duration)
    if not row:
        raise HTTPException(status_code=404, detail="Track or Artist not found")
    return dict(row)

# keyword is of type Union[str, None] --> optional 
# Annotated [] -> Additional validation so length doesnt exceed 40 characters 
@app.get("/search", response_model=dict)
async def search_tracks(
    keyword: Annotated[str | None, Query(min_length = 1, max_length=40)] = None, # {track title, album name, or artist name}
    track_name: Annotated[str | None, Query(min_length = 1, max_length=40)] = None,
    artist_name: Annotated[str | None, Query(min_length = 1, max_length=40)] = None,
    album_name: Annotated[str | None, Query(min_length = 1, max_length=40)] = None,
    db: asyncpg.Connection = Depends(get_db)
):

    # pre-process each input param 
    keyword = prepare_optional_string(keyword)
    track_name = prepare_optional_string(track_name)
    artist_name = prepare_optional_string(artist_name)
    album_name = prepare_optional_string(album_name)

    # check that keyword or track_name is present 
    if not keyword and not track_name:
        raise HTTPException(status_code=400, detail="At least one of 'keyword' or 'track_name' must be present")
    

    # query declaration 
    query = """
    SELECT
      tracks.id,
      tracks.name,
      tracks.artist_name,
      tracks.album_name,
      tracks.duration,
      lyrics.instrumental,
      lyrics.plain_lyrics,
      lyrics.synced_lyrics
    FROM
      tracks
      LEFT JOIN lyrics ON tracks.last_lyrics_id = lyrics.id
    WHERE
      tracks.id IN (
        SELECT
          rowid
        FROM
          tracks_fts
        WHERE
          tracks_fts MATCH ?
      )
    LIMIT 20
    """
    # execute query 
    row = await db.fetchrow(query, keyword, track_name, artist_name, album_name)
    if not row:
        raise HTTPException(status_code=404, detail="Track or Artist not found")
    return dict(row)

    conditions = []
    values = []
