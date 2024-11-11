import requests

# Rank parsing function
def get_rank(player_data):
    """Parse the player's rank and format it."""
    rank = None

    if 'rank' in player_data:
        rank = player_data['rank']
    elif 'monthlyPackageRank' in player_data:
        rank = player_data['monthlyPackageRank']
    elif 'newPackageRank' in player_data:
        rank = player_data['newPackageRank']
    elif 'packageRank' in player_data:
        rank = player_data['packageRank']

    if player_data.get('rank') == 'YOUTUBER':
        return '[YOUTUBE]'

    rank_dict = {
        'VIP': '[VIP]',
        'VIP_PLUS': '[VIP+]',
        'MVP': '[MVP]',
        'MVP_PLUS': '[MVP+]',
        'SUPERSTAR': '[MVP++]',  # MVP++ is known as SUPERSTAR in the API
    }

    return rank_dict.get(rank, '[Default]')  # Return default rank if none is found

def get_uuid(username):
    """Get UUID from Minecraft username."""
    url = f'https://api.mojang.com/users/profiles/minecraft/{username}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['id']
    else:
        print(f"Error: {username} not found.")
        return None

def get_bedwars_stats(uuid, api_key):
    """Fetch Bedwars stats and rank from Hypixel using UUID."""
    url = f'https://api.hypixel.net/player?key={api_key}&uuid={uuid}'
    response = requests.get(url)
    
    if response.status_code == 200:
        player_data = response.json()
        
        if player_data['player'] and 'stats' in player_data['player'] and 'Bedwars' in player_data['player']['stats']:
            bedwars_stats = player_data['player']['stats']['Bedwars']
            
            # Extract key Bedwars stats, including stars directly from achievements
            stats = {
                'rank': get_rank(player_data['player']),
                'stars': player_data['player'].get('achievements', {}).get('bedwars_level', 0),  # Correct way to get Bedwars stars
                'coins': bedwars_stats.get('coins', 0),
                'wins': bedwars_stats.get('wins_bedwars', 0),
                'losses': bedwars_stats.get('losses_bedwars', 0),
                'kills': bedwars_stats.get('kills_bedwars', 0),
                'deaths': bedwars_stats.get('deaths_bedwars', 0),
                'final_kills': bedwars_stats.get('final_kills_bedwars', 0),
                'final_deaths': bedwars_stats.get('final_deaths_bedwars', 0),
                'beds_broken': bedwars_stats.get('beds_broken_bedwars', 0),
                'beds_lost': bedwars_stats.get('beds_lost_bedwars', 0),
                'games_played': bedwars_stats.get('games_played_bedwars', 0),
            }
            return stats
        else:
            print("Bedwars stats not found for this player.")
            return None
    else:
        print("Failed to retrieve data from Hypixel API.")
        return None

def fetch_bedwars_stats(ign, hypixel_api_key):
    """Fetch and return Bedwars stats for a given Minecraft username."""
    uuid = get_uuid(ign)
    
    if uuid:
        stats = get_bedwars_stats(uuid, hypixel_api_key)
        if stats:
            return stats
        else:
            return "No Bedwars stats available."
    else:
        return "Invalid username."

# Example usage:
# Replace 'YourUsername' with the Minecraft username and 'YourHypixelApiKey' with your Hypixel API key
# stats = fetch_bedwars_stats('bedlessnoob', 'YourHypixelApiKey')
# print(stats)
