# Aurally_Sound_LRCLIB
FastAPI app to access a lyric database 

Command to run api:  uvicorn main:app --reload

API Documentation Link: http://127.0.0.1:8000/docs

Get lyrics by ID: 
GET /get/{id}
(working) 

Get lyrics with a track's signature: 
GET /get/{artist_name}/{track_name}/{album_name}/{duration}
(working)

