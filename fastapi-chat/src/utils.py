from uuid import UUID

import redis.asyncio as aioredis
from passlib.context import CryptContext

from src.models import User

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def _truncate_password(password: str) -> bytes:
    """Truncate password to 72 bytes for bcrypt, handling UTF-8 properly."""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) <= 72:
        return password_bytes
    
    # Truncate to 72 bytes
    password_bytes = password_bytes[:72]
    
    # Ensure we don't break UTF-8 encoding by removing bytes until valid
    while len(password_bytes) > 0:
        try:
            password_bytes.decode('utf-8')
            return password_bytes
        except UnicodeDecodeError:
            password_bytes = password_bytes[:-1]
    
    return b""


def get_hashed_password(password: str) -> str:
    # Truncate password to 72 characters (not bytes) for bcrypt compatibility
    # Using character truncation is simpler and avoids UTF-8 issues
    if len(password) > 72:
        password = password[:72]
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate password to 72 characters (not bytes) for bcrypt compatibility
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    return password_context.verify(plain_password, hashed_password)


async def clear_cache_for_get_messages(cache: aioredis.Redis, chat_guid: UUID):
    pattern_for_get_messages = f"messages_{chat_guid}_*"
    keys_found = cache.scan_iter(match=pattern_for_get_messages)
    async for key in keys_found:
        await cache.delete(key)


async def clear_cache_for_get_direct_chats(cache: aioredis.Redis, user: User):
    pattern_for_get_direct_chats = f"direct_chats_{user.guid}"
    keys_found = cache.scan_iter(match=pattern_for_get_direct_chats)
    async for key in keys_found:
        await cache.delete(key)


async def clear_cache_for_all_users(cache: aioredis.Redis):
    keys_found = cache.scan_iter(match="*all_users")
    async for key in keys_found:
        await cache.delete(key)
