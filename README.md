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
* Uses Postgres FTS method.

Tracks signature include the following information: id, track name, artist name, album name, duration, instrumental, plain lyrics, and synced lyrics. 

## Project structure (modules) 
###  api.py
* get_db() : Asychronous dependency that connects to the Postregre database. 
* prepare_input() : Preprocesses the input string by converting it to lowercase, removing special characters, and collapsing mulitple spaces into one 
 * Args : input(str): The input string to preprocess. 
 * Returns : str: The cleaned up string. 

* get_tracks_by_keyword : Searches for tracks in the database using full-text search on the provided keywords. If neither keyword or track name is provided, it returns an empty list. 

 * Args: 
  * q (Optional[str]): Keyword to search across all fields.
  * track_name (Optional[str]): Specific track name to search for.
  * artist_name (Optional[str]): Specific artist name to search for.
  * album_name (Optional[str]): Specific album name to search for.
  * conn (asyncpg.Connection): The database connection.

 * Returns: 
  *List[SimpleTrack]: A list of tracks that match the search criteria.

* get_info : Retrives track information by track ID. 

 *Args: 
  * id(int): The track ID.
  * db(asyncpg.Connection): The db connection dependency. 

 * Returns: 
  * dict: The track information. 


* read_track: retrieves the track info by artist name, track name, album name, and duration. 

 * Args: 

  * artist_name (str): the artist's name. 
  * track_name (str): the track's name. 
  * album_name (str): the album's name. 
  * duration(int): the duration of the track. 
  * db (asyncpg.Connection): the db connection dependency. 

 * Returns: 

  * dict: the track information. 

* search_tracks : Searches for tracks using optimal query parameters. 
 * Args: 
  * q (Optional[str]): Keyword to search across all fields.
  * track_name (Optional[str]): Specific track name to search for.
  * artist_name (Optional[str]): Specific artist name to search for.
  * album_name (Optional[str]): Specific album name to search for.

 * Returns: 
  * List[SimpleTrack]: A list of tracks that match the search criteria.

## database.py 
* connect_to_db(): establishes an asycn connection to the PostgreSQL DB/ 
 * This function uses the URL provided in the env and returns a connection object used to execute the queries. 
 * Rasies a asyncpg.PostgresError if theres an error connecting to the db.

* disconnect_from_db(): closes the async connection to the db. 
 * Args: conn - the db connection 


## models.py 
* SimpleLyrics(BaseModel) : Represents the lyrics informaton for the track 
** Attributes: 
*** plain_lyrics (Optional[str]): The plain text lyrics of the track. This field is optional and may be `None`.
*** synced_lyrics (Optional[str]): The synchronized lyrics of the track, often used for displaying lyrics in time with the music.This field is optional and may be `None`.
***instrumental (bool): A flag indicating whether the track is instrumental. Defaults to `False`.

* SimpleTrack(BaseModel): Represents basic info about the track. 
** Attributes:
*** id (int): The unique identifier for the track.
*** name (str): The name of the track.
*** artist_name (str): The name of the artist who performed the track.
*** lbum_name (str): The name of the album the track is part of.
*** duration (int): The duration of the track in seconds.
*** last_lyrics (Optional[SimpleLyrics]): The lyrics information for the track. This field is optional and may be `None`.
