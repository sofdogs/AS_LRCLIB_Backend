
import pytest
from fastapi.testclient import TestClient
from fastapi import Depends, HTTPException
from app.api import app, get_db
from unittest.mock import AsyncMock

# TestClient instance 
client = TestClient(app)

# unit test for get artist, track, album name and duration (all correct)
def test_get_all(): 
    response = client.get("/get/The Longest Johns/General Taylor/Between Wind And Water/198")
    print(response.json())
    assert response.status_code == 200 
    data = response.json() 
    assert data == {
        "id": 99,
        "name": "General Taylor",
        "artist_name": "The Longest Johns",
        "album_name": "Between Wind And Water",
        "duration": 197,
        "instrumental": False,
        "plain_lyrics": "General Taylor gained the day\n(Walk him along, John, carry him along)\nWell General Taylor gained the day\n(Carry him to his burying ground)\n\nTo me, way, hey, Stormy\nWalk him along, John, carry him along\nTo me, way, hey, Stormy\nCarry him to his burying ground\n\nWell I wish I was old Stormy's son\n(Walk him along, John, carry him along)\nI'd build a ship ten thousand tonne\n(Carry him to his burying ground)\n\nTo me, way, hey, Stormy\nWalk him along, John, carry him along\nTo me, way, hey, Stormy\nCarry him to his burying ground\n\nWe'll load her up with ale and rum\n(Walk him along, John, carry him along)\nThat every shellback should have some\n(Carry him to his burying ground)\n\nTo me, way, hey, Stormy\nWalk him along, John, carry him along\nTo me, way, hey, Stormy\nCarry him to his burying ground\n\nWe'll dig his grave with a silver spade\n(Walk him along, John, carry him along)\nHis shroud of finest silk is made\n(Carry him to his burying ground)\n\nTo me, way, hey, Stormy\nWalk him along, John, carry him along\nTo me, way, hey, Stormy\nCarry him to his burying ground\n\nWe'll lower him down on a golden chain\n(Walk him along, John, carry him along)\nOn every link we'll carve his name\n(Carry him to his burying ground)\n\nTo me, way, hey, Stormy\nWalk him along, John, carry him along\nTo me, way, hey, Stormy\nCarry him to his burying ground\n\nWell General Taylor's dead and gone\n(Walk him along, John, carry him along)\nWell General Taylor's dead and gone\n(Carry him to his burying ground)\n\nTo me, way, hey, Stormy\nWalk him along, John, carry him along\nTo me, way, hey, Stormy\nCarry him to his burying ground",
        "synced_lyrics": "[00:01.56] General Taylor gained the day\n[00:03.97] (Walk him along, John, carry him along)\n[00:07.85] Well General Taylor gained the day\n[00:11.42] (Carry him to his burying ground)\n[00:15.68] To me, way, hey, Stormy\n[00:19.93] Walk him along, John, carry him along\n[00:23.69] To me, way, hey, Stormy\n[00:27.94] Carry him to his burying ground\n[00:31.92] Well I wish I was old Stormy's son\n[00:35.18] (Walk him along, John, carry him along)\n[00:39.70] I'd build a ship ten thousand tonne\n[00:43.30] (Carry him to his burying ground)\n[00:47.22] To me, way, hey, Stormy\n[00:51.52] Walk him along, John, carry him along\n[00:55.32] To me, way, hey, Stormy\n[00:59.61] Carry him to his burying ground\n[01:03.39] We'll load her up with ale and rum\n[01:07.16] (Walk him along, John, carry him along)\n[01:11.06] That every shellback should have some\n[01:14.95] (Carry him to his burying ground)\n[01:17.92] To me, way, hey, Stormy\n[01:23.38] Walk him along, John, carry him along\n[01:27.12] To me, way, hey, Stormy\n[01:30.92] Carry him to his burying ground\n[01:35.14] We'll dig his grave with a silver spade\n[01:38.95] (Walk him along, John, carry him along)\n[01:42.81] His shroud of finest silk is made\n[01:46.65] (Carry him to his burying ground)\n[01:50.49] To me, way, hey, Stormy\n[01:54.23] Walk him along, John, carry him along\n[01:58.36] To me, way, hey, Stormy\n[02:02.85] Carry him to his burying ground\n[02:06.70] We'll lower him down on a golden chain\n[02:10.53] (Walk him along, John, carry him along)\n[02:14.36] On every link we'll carve his name\n[02:18.18] (Carry him to his burying ground)\n[02:22.45] To me, way, hey, Stormy\n[02:26.57] Walk him along, John, carry him along\n[02:30.20] To me, way, hey, Stormy\n[02:34.37] Carry him to his burying ground\n[02:38.63] Well General Taylor's dead and gone\n[02:42.80] (Walk him along, John, carry him along)\n[02:46.68] Well General Taylor's dead and gone\n[02:50.56] (Carry him to his burying ground)\n[02:54.63] To me, way, hey, Stormy\n[02:58.40] Walk him along, John, carry him along\n[03:02.85] To me, way, hey, Stormy\n[03:06.52] Carry him to his burying ground\n[03:14.97] "
    }

# unit test for each 4 input fields incorrect
def test_get_all_no_match(): 
    response = client.get("/get/unknown artist/unknown track/unknown album/300")
    assert response.status_code == 404
    assert response.json() == {"detail": "Track or Artist not found"}

# unit test for album name input field incorrect
def test_get_all_invalid_album_name(): 
    response = client.get("/get/The Longest Johns/General Taylor/Between Water and Wind/197")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Track or Artist not found"}

# unit test for artist name input field incorrect
def test_get_all_invalid_artist_name(): 
    response = client.get("/get/The Johns Longest/General Taylor/Between Wind and Water/197")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Track or Artist not found"}

# unit test for track name input field incorrect
def test_get_all_invalid_track_name(): 
    response = client.get("/get/The Longest Johns/General T/Between Wind and Water/197")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Track or Artist not found"}

# unit test for duration name input field incorrect
def test_get_all_invalid_duation(): 
    response = client.get("/get/The Longest Johns/General Taylor/Between Wind and Water/201")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Track or Artist not found"}

# unit test for duration being a string 
def test_get_all_invalid_type(): 
    response = client.get("/get/The Longest Johns/General Taylor/Between Wind and Water/hello")
    assert response.status_code == 422 