import discord
from skyblock.fetch_profiles import fetch_profiles
from skyblock.fetch_networth import fetch_networth, format_networth
from skyblock.get_hotm import get_hotm_data
from skyblock.calculate_skill_average import get_skill_data
from skyblock.format_slayers import format_slayers
from skyblock.uuid import get_uuid
from skyblock.dungeon import get_catacombs_data

# You may need to define or import this helper function to format large numbers
def format_large_number(number):
    return f"{number:,}"  # Simple number formatting for large numbers

async def create_skyblock_embed(api_key: str, username: str, profile: str = None, price: int = 0, payment_method: str = ""):
    uuid = get_uuid(username)
    if not uuid:
        embed = discord.Embed(
            title="Error",
            description="Could not retrieve UUID. Please check the IGN.",
            color=discord.Color.red()
        )
        return embed, {}

    # Fetch profiles
    profiles, player = await fetch_profiles(username, api_key)
    if not profiles:
        embed = discord.Embed(
            title="Error",
            description=f"No profiles found for {username}.",
            color=discord.Color.red()
        )
        return embed, {}

    # If a profile is provided, use that, otherwise default to the first profile
    profile_name = profile if profile in profiles else profiles[0]

    # Select the profile and initialize it
    profile_data = player.select_profile(profile_name)
    await profile_data.init()

    # Fetch data
    networth_data = await fetch_networth(uuid, profile_name)
    skill_levels, skill_experience, skill_average = get_skill_data(profile_data)
    catacombs_level, cata_exp = get_catacombs_data(profile_data)
    hotm_level, mithril_powder, gemstone_powder = await get_hotm_data(profile_data)
    formatted_slayers = format_slayers(profile_data.slayer_data)
    formatted_networth = format_networth(networth_data)
    level = profile_data.skyblock_level

    # Create the stats dictionary to save in the database
    stats = {
        'skill_average': skill_average,
        'catacombs_level': catacombs_level,
        'slayer_levels': formatted_slayers,
        'hotm_level': hotm_level,
        'mithril_powder': mithril_powder,
        'gemstone_powder': gemstone_powder,
        'networth_total': formatted_networth['formatted_total'],
        'networth_bank': formatted_networth['formatted_bank'],
        'networth_purse': formatted_networth['formatted_purse'],
        'networth_soulbound': formatted_networth['formatted_soulbound'],
        'cata_exp': cata_exp,
        'skyblock_level': level  # Assuming you can get SkyBlock level from player data
    }

    # Create embed with your updated format
    embed = discord.Embed(
        title=f"SkyBlock Statistics",
        color=discord.Color.from_rgb(47, 49, 54)
    )
    embed.set_thumbnail(url="https://mc-heads.net/body/Anonymous/left")

    # Adding the overall stats field
    embed.add_field(
        name="<:1236755617918619751:1289571636382666843> **Overall Stats**",
        value=(
            f"**Skill Average:** {skill_average:.0f}\n"
            f"**Catacombs Level:** {int(catacombs_level)}\n"
            f"**Slayer Levels:** {formatted_slayers}\n"
            f"**SkyBlock Level:** {level:.0f}"
        ),
        inline=False
    )

    # Adding the networth field
    embed.add_field(
        name="<:1236756044588253184:1289571640702926878> **Networth**",
        value=(
            f"**Total Networth:** {formatted_networth['formatted_total']}\n"
            f"**Bank + Purse:** {formatted_networth['formatted_bank']} + {formatted_networth['formatted_purse']} Coins\n"
            f"**Soulbound Networth:** {formatted_networth['formatted_soulbound']}"
        ),
        inline=False
    )

    # Adding mining stats
    embed.add_field(
        name="<:1236755172139728997:1289571625666347110> **Mining Stats**",
        value=(
            f"**Heart of the Mountain Level:** {hotm_level}\n"
            f"**Mithril Powder:** {format_large_number(mithril_powder)}\n"
            f"**Gemstone Powder:** {format_large_number(gemstone_powder)}"
        ),
        inline=False
    )

    # Adding price and payment methods
    embed.add_field(
        name="<:money:1291077341950509167> **Price**",
        value=f"{price} USD",  # Display the price here
        inline=True
    )
    embed.add_field(
        name="<:PaypalLogo:1291077487207383061> **Payment Methods**",
        value=f"{payment_method}",
        inline=False
    )

    # Return the embed and stats for saving
    return embed, stats
