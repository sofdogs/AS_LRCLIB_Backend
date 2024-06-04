# Aurally_Sound_LRCLIB
FastAPI app to access a PostgreSQL lyric database. 

## Tools to Run: 

Command to run api:  uvicorn api:app --reload
Run entry point from console: python main.py
API Documentation Link: http://127.0.0.1:8000/docs
Front end port: localhost:3000

## Endpoints

Endpoints define the the operations that can be performed on the database. The following are the current endpoints: 

* GET /get/{id} - get a track's signature from a specific track id. 

Get lyrics with a track's signature: 
* GET /get/{artist_name}/{track_name}/{album_name}/{duration} - get a track's signature through an artist name, track name, allbum name, and duration. (currently, is case sensitive.)

tracks signature include the following information: id, track name, artist name, album name, duration, instrumental, plain lyrics, and synced lyrics. 

## Project structure (modules) 
