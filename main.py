from fastapi import FastAPI, HTTPException, Depends
import asyncpg
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

# create app
app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

# Dependency
async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

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

@app.get("/get/{artist_name}/{name}/{album_name}/{duration}",response_model = dict)
async def read_track(artist_name: str, name: str, album_name: str, duration: int, db: asyncpg.Connection = Depends(get_db)):
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
        artist_name =  $1 AND 
        album_name = $2 AND 
        name = $3 AND 
        duration = $4
    """
    row = await db.fetchrow(query, artist_name, name, album_name, duration)
    if not row:
        raise HTTPException(status_code=404, detail="Track or Artist not found")
    return dict(row)

