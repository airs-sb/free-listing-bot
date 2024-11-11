import requests
from skyblockparser.profile import SkyblockParser
from .uuid import get_uuid

async def fetch_profiles(ign, api_key):
    uuid = get_uuid(ign)
    if not uuid:
        return [], None  # Return empty list if UUID not found

    url = f"https://api.hypixel.net/v2/skyblock/profiles?key={api_key}&uuid={uuid}"
    response = requests.get(url).json()

    player = SkyblockParser(response, uuid, api_key)
    return player.get_profiles(), player
