import asyncio
import json


async def notify_users(payload, users=None):
    if users is None:
        users = WEBSOCKET_INFO_DICT.keys()
    await asyncio.wait([user.send(payload) for user in users])


def cleanup_redis_dict(dict_from_redis):
    return {k.decode('utf8'): v.decode('utf8') for k, v in dict_from_redis.items()}


def transform_to_redis_safe_dict(dict_with_nones):
    # this will turn any toplevel None values -> 'null'
    return {k: 'null' if v is None else v for k, v in dict_with_nones.items()}
