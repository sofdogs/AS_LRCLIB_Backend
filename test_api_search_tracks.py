
import pytest
from fastapi.testclient import TestClient
from fastapi import Depends, HTTPException
from app.api import app, get_db
from unittest.mock import AsyncMock

# TestClient instance 
client = TestClient(app)

def test_search_tracks(): 
    params = { 
        "q": "Taylor Swift "
    }

    response = client.get("/tracks", params = params) 

    assert response.status_code == 200 

    data = response.json() 

    assert len(data) == 20 

    for item in data:
        assert "id" in item
        assert "name" in item
        assert "artist_name" in item
        assert "album_name" in item
        assert "duration" in item
        assert "instrumental" in item
        assert "plain_lyrics" in item
        assert "synced_lyrics" in item
