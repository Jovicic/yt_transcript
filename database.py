import aiosqlite
import json
import os
from typing import Optional

DB_PATH = os.getenv("DB_PATH", "transcripts.db")

async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        yield db

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                video_id TEXT PRIMARY KEY,
                content TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS api_tokens (
                token TEXT PRIMARY KEY
            )
        """)
        await db.commit()

async def get_cached_transcript(video_id: str) -> Optional[list]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT content FROM transcripts WHERE video_id = ?", (video_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0])
    return None

async def save_transcript(video_id: str, content: list):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO transcripts (video_id, content) VALUES (?, ?)",
            (video_id, json.dumps(content))
        )
        await db.commit()

async def is_token_valid(token: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM api_tokens WHERE token = ?", (token,)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def add_token(token: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO api_tokens (token) VALUES (?)", (token,))
        await db.commit()

async def has_any_token() -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM api_tokens LIMIT 1") as cursor:
            row = await cursor.fetchone()
            return row is not None
