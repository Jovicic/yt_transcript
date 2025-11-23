import pytest
import database
import aiosqlite
from main import app, lifespan

@pytest.mark.asyncio
async def test_lifespan_generates_token_if_none_exist(capsys):
    async with aiosqlite.connect(database.DB_PATH) as db:
        await db.execute("DELETE FROM api_tokens")
        await db.commit()

    # Verify it's empty
    assert not await database.has_any_token()

    # Run lifespan
    async with lifespan(app):
        pass

    # Verify a token was added
    assert await database.has_any_token()

    # Verify the token details
    async with aiosqlite.connect(database.DB_PATH) as db:
        async with db.execute("SELECT token FROM api_tokens") as cursor:
            rows = await cursor.fetchall()
            rows = list(rows)
            assert len(rows) == 1
            token = rows[0][0]
            # secrets.token_urlsafe(32) produces approx 43 chars
            assert len(token) > 30

    # Verify the output was printed
    captured = capsys.readouterr()
    assert "WARNING: No API tokens found. Generated a new secure token:" in captured.out
    assert f"Token: {token}" in captured.out

@pytest.mark.asyncio
async def test_lifespan_does_not_generate_token_if_exists(capsys):
    assert await database.has_any_token()

    # Run lifespan
    async with lifespan(app):
        pass

    async with aiosqlite.connect(database.DB_PATH) as db:
        async with db.execute("SELECT token FROM api_tokens") as cursor:
            rows = await cursor.fetchall()
            rows = list(rows)
            assert len(rows) == 1
            assert rows[0][0] == "test-token"

    # Verify no warning was printed
    captured = capsys.readouterr()
    assert "WARNING: No API tokens found" not in captured.out
