import os
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from main import app
import database

# Use a file-based DB for tests so connections share state
TEST_DB = "test_transcripts.db"

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    """
    Overrides the database path and initializes a fresh DB for each test function.
    """
    # Override the DB_PATH in the database module
    original_db_path = database.DB_PATH
    database.DB_PATH = TEST_DB

    # Clean up any existing test db
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Initialize schema
    await database.init_db()
    # Add a default token for testing
    await database.add_token("test-token")

    yield

    # Teardown: remove the test database file
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Restore original path (though not strictly necessary if process dies)
    database.DB_PATH = original_db_path

@pytest.fixture
def client():
    """
    Returns a TestClient instance.
    """
    return TestClient(app)
