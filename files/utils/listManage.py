import discord
import random
import json
from utils.skyblock_embed import create_skyblock_embed
from utils.database import insert_account  # Import database function
from utils.listViews import ListViews  # Import the views
import sqlite3

# Load config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

async def list_setup(ctx, price: int, ign: str, api_key: str, payment_method: str, additional_info: str = None, profile: str = None):
    # Pass the price and payment method to create_skyblock_embed
    skyblock_embed, stats = await create_skyblock_embed(api_key, ign, profile, price=price, payment_method=payment_method)

    # Create an additional info embed
    additional_embed = discord.Embed(
        title="Additional Information",
        description=additional_info if additional_info else "No additional information provided.",
        color=discord.Color.blue()
    )
    additional_embed.add_field(
        name="Listed By",
        value=f"<@{ctx.author.id}>",
        inline=False
    )
    additional_embed.set_footer(
        text="Made By airsbw | https://blazecoins.net",
        icon_url="https://images-ext-1.discordapp.net/external/p4mQq0j6A_tLFlpktZMDz8uzhy7ksxUjdTaYw-vVnc0/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/463798421074214914/424f24568e095f05ca84a02c3c75aaae.png"
    )

    # Retrieve the accounts category from the guild using the category ID from config
    category_id = config["accounts_category"]
    category = discord.utils.get(ctx.guild.categories, id=int(category_id))

    if category is None:
        await ctx.send("Category not found! Please ensure the category ID is correct in config.json.")
        return

    # Create the new channel in the specified category
    number = random.randint(1000, 9999)
    channel_name = f"💲{price}┃account-{number}"
    channel = await ctx.guild.create_text_channel(name=channel_name, category=category)

    # Create the view (with buttons)
    view = ListViews()

    # Send embeds in the new channel with the views (buttons)
    await channel.send(embed=skyblock_embed)
    await channel.send(embed=additional_embed, view=view)

    # Restrict permissions so no one can type or react
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    overwrite.add_reactions = False
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    # Save the data, including stats, to the database
    insert_account(
        owner_id=str(ctx.author.id),
        price=price,
        ign=ign,
        api_key=api_key,
        payment_method=payment_method,
        additional_info=additional_info,
        profile=profile,
        channel_id=str(channel.id),
        channel_name=channel_name,
        stats=stats  # The fetched Skyblock stats
    )


    return channel

