import asyncpg
import os
from dotenv import load_dotenv

load_dotenv() # load env

DATABASE_URL = os.getenv("DATABASE_URL")

async def connect_to_db():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

async def disconnect_from_db(conn):
    await conn.close()
