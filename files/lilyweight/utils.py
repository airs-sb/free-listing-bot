import aiohttp

from lilyweight.constants import skill_XP_per_level


def get_level_from_XP(xp: int) -> int:
    xp_added = 0
    for i, i_xp in enumerate(skill_XP_per_level):
        xp_added += i_xp
        if xp < xp_added:
            return int((i - 1) + (xp - (xp_added - i_xp)) / i_xp)
    return 60


def get_xp_from_level(level: int) -> int:
    return sum(skill_XP_per_level[0: level + 1])


async def get_profile(uuid: str, api_key: str, session: aiohttp.ClientSession, cute_name: str = None) -> dict:
    async with session.get("https://api.hypixel.net/skyblock/profiles", params={
        "key": api_key,
        "uuid": uuid
    }) as r:
        response_json = await r.json()

        if cute_name:
            try:
                return [
                    profile for profile in response_json.get("profiles", []) if profile["cute_name"] == cute_name
                ][0]["members"][uuid]
            except IndexError:
                raise ValueError(f"Could not find profile with cute name {cute_name}")

        return sorted(
            response_json.get("profiles", []), key=lambda x: x["members"][uuid]["last_save"]
        )[-1]["members"][uuid]


async def get_player(uuid: str, api_key: str, session: aiohttp.ClientSession):
    async with session.get("https://api.hypixel.net/player", params={
        "key": api_key,
        "uuid": uuid
    }) as r:
        return (await r.json())["player"]


async def get_uuid(username: str, session: aiohttp.ClientSession):
    async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as r:
        return (await r.json())["id"]


async def get_username(uuid: str, session: aiohttp.ClientSession):
    async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{uuid}") as r:
        return (await r.json())[-1]["name"]
