from fastapi import FastAPI, HTTPException, Depends, Query
import asyncpg
import re
from typing import List, Optional, Annotated
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from .database import connect_to_db, disconnect_from_db
from .models import SimpleTrack, SimpleLyrics
from psycopg2.extras import RealDictCursor

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
    "http://192.168.86.157:3000",
    "http://192.168.1.237:3000",
    "http://192.168.86.44:3000"
]

# enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Dependency 
async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# preprocessing the string by striping
# whitespace and converting to lowercase
def prepare_input(input: str) -> str: 
    input = input.lower()
    input = re.sub(r"[`~!@#$%^&*()_|+\-=?;:,.<>{}\[\]\\\/]", " ", input)
    input = re.sub(r"['’]", "", input)
    
    # Collapse multiple spaces into a single space
    input = ' '.join(input.split())

    return input

# preprocessing the optional strings 
def prepare_optional_string(s: Optional[str]) -> Optional[str]:
    if s is None: 
        return None
    processed_val = prepare_input(s)
    if not processed_val: 
        return None
    return processed_val

async def get_tracks_by_keyword(
    q: Optional[str],
    track_name: Optional[str],
    artist_name: Optional[str],
    album_name: Optional[str],
    conn: asyncpg.Connection
) -> List[SimpleTrack]:

    # preprocessing input...
    q = prepare_input(q) if q else None
    track_name = prepare_input(track_name) if track_name else None
    artist_name = prepare_input(artist_name) if artist_name else None
    album_name = prepare_input(album_name) if album_name else None

    if not q and not track_name:
        return []

    # Using PostgreSQL full-text search syntax with to_tsvector and to_tsquery
    if q:
        fts_query = ' & '.join(q.split())
    else:
        fts_query = ' & '.join(filter(None, [track_name, artist_name, album_name]))

    
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
      to_tsvector('english', coalesce(tracks.name_lower, '') || ' ' || coalesce(tracks.artist_name_lower, '') || ' ' || coalesce(tracks.album_name_lower, '')) @@ to_tsquery($1)
    LIMIT 20
    """
    print(f"FTS query: {fts_query}")

    try: 
        rows = await conn.fetch(query, fts_query)

        if not rows:
            return []
         
        print("Fetched rows:")
        for row in rows:
            print(row)
        
        tracks = []
        for row in rows:
            last_lyrics = SimpleLyrics(
                plain_lyrics=row['plain_lyrics'] or "",  # empty string is instrumental is TRUE
                synced_lyrics=row['synced_lyrics'] or "",  # empty string is instrumental is TRUE
                instrumental=row['instrumental'] if row['instrumental'] is not None else False
            )
            track = SimpleTrack(
                id=row['id'],
                name=row['name'],
                artist_name=row['artist_name'],
                album_name=row['album_name'],
                duration=row['duration'],
                last_lyrics=last_lyrics
            )
            tracks.append(track)

        return tracks
    except Exception as e:
        print(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



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
        duration BETWEEN $4-2 AND $4+2
    ORDER BY
        t.id
    """
    row = await db.fetchrow(query, artist_name, track_name, album_name, duration)
    if not row:
        raise HTTPException(status_code=404, detail="Track or Artist not found")
    return dict(row)



@app.get("/tracks", response_model=List[SimpleTrack])
async def search_tracks(
    q: Optional[str] = Query(None, min_length=1, max_length=50),
    track_name: Optional[str] = Query(None, min_length=1, max_length=50),
    artist_name: Optional[str] = Query(None, min_length=1, max_length=50),
    album_name: Optional[str] = Query(None, min_length=1, max_length=50)
):
    conn = await connect_to_db()
    try:
        tracks = await get_tracks_by_keyword(q, track_name, artist_name, album_name, conn)
        return tracks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await disconnect_from_db(conn)







'''
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
    conditions = []
    values = []

    if keyword:
        conditions.append("(t.name ILIKE $1 OR t.artist_name ILIKE $1 OR t.album_name ILIKE $1)")
        values.append(f"%{keyword}%")
    if track_name:
        conditions.append("t.name ILIKE $2")
        values.append(f"%{track_name}%")
    if artist_name:
        conditions.append("t.artist_name ILIKE $3")
        values.append(f"%{artist_name}%")
    if album_name:
        conditions.append("t.album_name ILIKE $4")
        values.append(f"%{album_name}%")

    
    # execute query 
    row = await db.fetchrow(query, keyword, track_name, artist_name, album_name)
    if not row:
        raise HTTPException(status_code=404, detail="Track or Artist not found")
    return dict(row)
'''