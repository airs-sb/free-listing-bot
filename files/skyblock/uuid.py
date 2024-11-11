import requests

def get_uuid(ign):
    """Retrieve the UUID for a given IGN."""
    uuid_url = f"https://api.mojang.com/users/profiles/minecraft/{ign}"
    uuid_response = requests.get(uuid_url).json()
    return uuid_response.get("id")
