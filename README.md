# Aurally_Sound_LRCLIB
FastAPI app to access a PostgreSQL lyric database. 

## Tools to Run: 

Run entry point from console: python main.py

API Documentation Link: http://127.0.0.1:8000/docs

Front end port: localhost:3000

## Endpoints
Endpoints define the the operations that can be performed on the database. The following are the current endpoints: 

Get Track's Signature by ID: 
* GET /get/{id} - get a track's signature from a specific track id. 

Get Track's Signature by Details 
* All three parameters are required: 'artist_name', 'track_name', 'album_name', 'duration'. 
* GET /get/{artist_name}/{track_name}/{album_name}/{duration} - get a track's signature through an artist name, track name, allbum name, and duration. 
** NOT case sensitve. 

Search Track's Signatures by Keywords: 
* GET /tracks searches for tracks based on query parameters: 'q', 'track_name', 'artist_name', and 'album_name'.
* Parameters 'q' OR 'track_name' must be present.
* Returns a list of maximum 20 'SimpleTrack' objects or raises an error if query fails.

Tracks signature include the following information: id, track name, artist name, album name, duration, instrumental, plain lyrics, and synced lyrics. 

## Project structure (modules) 
