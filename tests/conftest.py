import os
import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from typing import Generator

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

@pytest.fixture
def mock_db_session() -> MagicMock:
    """Create a mock database session"""
    session = MagicMock(spec=Session)
    return session

@pytest.fixture
def mock_query() -> MagicMock:
    """Create a mock query object"""
    query = MagicMock()
    query.filter.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    query.all.return_value = []
    query.count.return_value = 0
    return query

@pytest.fixture
def mock_db_session_with_query(mock_db_session: MagicMock, mock_query: MagicMock) -> MagicMock:
    """Create a mock database session with a query method"""
    mock_db_session.query.return_value = mock_query
    return mock_db_session