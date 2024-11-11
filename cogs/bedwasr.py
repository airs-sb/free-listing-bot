import requests

API_KEY = '014998aa-67fb-44ff-9e9c-91f8d2bfc2ae'  # Replace this with your Hypixel API key

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

def get_bedwars_stats(uuid):
    """Fetch Bedwars stats and rank from Hypixel using UUID."""
    url = f'https://api.hypixel.net/player?key={API_KEY}&uuid={uuid}'
    response = requests.get(url)
    
    if response.status_code == 200:
        player_data = response.json()
        
        if player_data['player'] and 'stats' in player_data['player'] and 'Bedwars' in player_data['player']['stats']:
            bedwars_stats = player_data['player']['stats']['Bedwars']
            
            # Extract key Bedwars stats
            stats = {
                'rank': get_rank(player_data['player']),
                'stars': bedwars_stats.get('Experience', 0) // 1000,  # Bedwars level is experience divided by 1000
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

def display_stats(username):
    """Display Bedwars stats for a given username."""
    uuid = get_uuid(username)
    
    if uuid:
        stats = get_bedwars_stats(uuid)
        if stats:
            print(f"Bedwars Stats for {username}:")
            print(f"Rank: {stats['rank']}")
            print(f"Stars: {stats['stars']} ⭐")
            for stat, value in stats.items():
                if stat not in ['rank', 'stars']:
                    print(f"{stat.capitalize().replace('_', ' ')}: {value}")
        else:
            print("No Bedwars stats available.")
    else:
        print("Invalid username.")

# Replace 'YourUsername' with the Minecraft username you want to fetch stats for
username = 'meyser'
display_stats(username)
