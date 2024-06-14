
import pytest
from fastapi.testclient import TestClient
from fastapi import Depends, HTTPException
from app.api import app, get_db
from unittest.mock import AsyncMock

# TestClient instance 
client = TestClient(app)
