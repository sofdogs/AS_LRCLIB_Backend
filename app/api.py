from fastapi import FastAPI, HTTPException, Depends
import asyncpg
from typing import List
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
    JOIN lyrics l on t.id = l.id
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
    JOIN lyrics l on t.id = l.id
    WHERE 
        artist_name_lower =  $1 AND 
        name_lower = $2 AND  
        album_name_lower = $3 AND 
        duration = $4
    """
    row = await db.fetchrow(query, artist_name, track_name, album_name, duration)
    if not row:
        raise HTTPException(status_code=404, detail="Track or Artist not found")
    return dict(row)
