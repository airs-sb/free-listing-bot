import discord
from bedwars.bedwars import fetch_bedwars_stats  # Assuming this is your file containing the stats fetching code

# Function to create the Bedwars embed
def create_bedwars_embed(api_key: str, ign: str, price: int, payment_method: str):
    """
    Creates a Discord Embed for Bedwars stats based on the provided IGN and Hypixel API key.

    Args:
        ign (str): Minecraft username (IGN).
        api_key (str): Hypixel API key.
        price (int): Price for the listing.
        payment_method (str): Payment method for the listing.

    Returns:
        discord.Embed: A Discord embed object containing Bedwars stats.
        stats (dict): Dictionary of Bedwars stats for saving to the database.
    """
    # Fetch real Bedwars stats from Hypixel API
    stats = fetch_bedwars_stats(ign, api_key)

    if isinstance(stats, str):
        # If stats fetching returned an error message, create an error embed
        embed = discord.Embed(
            title=f"Error fetching stats for {ign}",
            description=stats,
            color=discord.Color.red()
        )
        return embed, {}

    # Create the embed with the stats and listing details
    embed = discord.Embed(
        title=f"Bedwars Stats",
       
        color=discord.Color.blue()
    )

    # Add the stats to the embed
    embed.add_field(name="<:5526bluestar:1291711175557513332> Overall Stats", value=f'''
**Rank:** {stats['rank']}
**Stars:** {stats['stars']}
**Wins:** {stats['wins']:,}

''', inline=True)
    embed.add_field(name="<:final_death:1291711325117878365> Kills / Deaths", value=f'''
**Kills:** {stats['kills']:,}
**Deaths:** {stats['deaths']:,}
**Final Kills:** {stats['final_kills']:,}
**Final Deaths:** {stats['final_deaths']:,}
''', inline=False)



    embed.add_field(name="<:1236755172139728997:1289571625666347110> Other Stats", value=f'''
**Losses:** {stats['losses']:,}
**Beds Broken:** {stats['beds_broken']:,}
**Beds Lost:** {stats['beds_lost']:,}
**Games Played:** {stats['games_played']:,}




''', inline=False)

    embed.add_field(name="<:money:1291077341950509167> Price", value=f"{price}", inline=False)
    embed.add_field(name="<:PaypalLogo:1291077487207383061> Payment Method", value=f"{payment_method}", inline=False)
    embed.set_thumbnail(url="https://mc-heads.net/body/Anonymous/left")


    return embed, stats
