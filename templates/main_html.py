from fastapi import FastAPI, HTTPException, Depends,Request
import asyncpg
from typing import List
import os
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
"""

# load the .env file
load_dotenv()

# load html templates
templates =  Jinja2Templates(directory='templates/')

# create app
#app = FastAPI()

# load database url 
DATABASE_URL = os.getenv("DATABASE_URL")


# Dependency
async def get_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

# root connection 
@app.get('/')
async def read_root(request: Request): 
    return templates.TemplateResponse("form.html", context =  {"request": request})

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
@app.get('/get_info', response_class = HTMLResponse)
async def get_info(request: Request, id: int, db: asyncpg.Connection = Depends(get_db)):
    query = 
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

    row = await db.fetchrow(query, id)
    if not row: 
        raise HTTPException(status_code=404, detail="Track not found")
    return templates.TemplateResponse("form.html", context = {"request": request, "result": row })


@app.get("/get_track",response_class = HTMLResponse)
async def read_track(request: Request, artist_name: str, track_name: str, album_name: str, duration: int, db: asyncpg.Connection = Depends(get_db)):
    query =
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
        name = $2 AND  
        album_name = $3 AND 
        duration = $4

    row = await db.fetchrow(query, artist_name, track_name, album_name, duration)
    if not row:
        raise HTTPException(status_code=404, detail="Track or Artist not found")
    return templates.TemplateResponse("form.html", context = {"request": request, "result": row })

"""