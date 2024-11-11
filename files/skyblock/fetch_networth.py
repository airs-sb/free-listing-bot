import requests

async def fetch_networth(uuid, profile_name):
    """Fetch networth data from SkyCrypt for the given UUID and profile name."""
    try:
        url = f"https://sky.shiiyu.moe/api/v2/profile/{uuid}"
        response = requests.get(url).json()

        profile_data = None
        for profile in response.get("profiles", {}).values():
            if profile.get("cute_name", "").lower() == profile_name.lower():
                profile_data = profile
                break

        if not profile_data:
            print(f"Profile '{profile_name}' not found for UUID {uuid}.")
            return None

        if 'data' in profile_data and 'networth' in profile_data['data']:
            return profile_data['data']['networth']
        else:
            print(f"Networth data not found in 'data' of profile '{profile_name}'.")
            return None
    except Exception as e:
        print(f"Error fetching networth data: {e}")
        return None

def format_networth(networth_data):
    """Format net worth and coins for better readability."""
    networth_total = networth_data.get('networth', 0)
    unsoulbound_networth = networth_data.get('unsoulboundNetworth', 0)
    purse = networth_data.get('purse', 0)
    bank = networth_data.get('bank', 0)

    # Calculate soulbound networth
    soulbound_networth = networth_total - unsoulbound_networth

    return {
        "formatted_total": format_large_number(networth_total),
        "formatted_soulbound": format_large_number(soulbound_networth),
        "formatted_purse": format_large_number(purse),
        "formatted_bank": format_large_number(bank),
    }

def format_large_number(num):
    """Formats large numbers for better readability."""
    num = float(num)  # Ensure num is a float
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    return str(round(num, 2))  # Round to 2 decimal places
