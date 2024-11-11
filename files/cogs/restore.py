import discord
from discord.ext import commands
from utils.database import fetch_all_accounts
from utils.listViews import ListViews  # Import the views
import json

# Load the config file and access role
with open('config.json') as config_file:
    config = json.load(config_file)
    ACCESS_ROLE_ID = config["access_role"]  # Fetch the access role ID
    ACCOUNTS_CATEGORY_ID = config["accounts_category"]  # Fetch the category ID for accounts

# Helper function to format large numbers
def format_large_number(number):
    return f"{number:,}"

class RestoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="restore-skyblock")
    async def restore_accounts(self, ctx):
        """
        Command to restore all the listed accounts and recreate their channels and embeds.
        """
        # Fetch the access role from the config
        access_role = discord.utils.get(ctx.guild.roles, id=ACCESS_ROLE_ID)

        # Check if the user has the access role
        if access_role in ctx.author.roles:
            # Proceed with the restoration if the user has the required role

            accounts = fetch_all_accounts()

            # Retrieve the accounts category from the guild using the category ID from config
            category = discord.utils.get(ctx.guild.categories, id=int(ACCOUNTS_CATEGORY_ID))

            if category is None:
                await ctx.respond("Accounts category not found! Please ensure the category ID is correct in config.json.", ephemeral=True)
                return

            for account in accounts:
                (owner_id, price, ign, api_key, payment_method, additional_info, profile, channel_id, channel_name,
                skill_average, catacombs_level, slayer_levels, hotm_level, mithril_powder, gemstone_powder, networth_total, networth_bank, networth_purse, networth_soulbound) = account[1:]

                # Create the SkyBlock stats embed
                embed = discord.Embed(
                    title=f"Skyblock Statistics",
                    color=discord.Color.from_rgb(47, 49, 54)
                )
                embed.set_thumbnail(url="https://mc-heads.net/body/Anonymous/left")

                # Overall stats
                embed.add_field(
                    name="<:1236755617918619751:1289571636382666843> **Overall Stats**",
                    value=(
                        f"**Skill Average:** {skill_average:.0f}\n"
                        f"**Catacombs Level:** {int(catacombs_level)}\n"
                        f"**Slayer Levels:** {slayer_levels}\n"
                        f"**SkyBlock Level:** N/A"  # Assuming SkyBlock level is not available in the restore data
                    ),
                    inline=False
                )

                # Networth stats
                embed.add_field(
                    name="<:1236756044588253184:1289571640702926878> **Networth**",
                    value=(
                        f"**Total Networth:** {networth_total}\n"
                        f"**Bank + Purse:** {networth_bank} + {networth_purse} Coins\n"
                        f"**Soulbound Networth:** {networth_soulbound}"
                    ),
                    inline=False
                )

                # Mining stats
                embed.add_field(
                    name="<:1236755172139728997:1289571625666347110> **Mining Stats**",
                    value=(
                        f"**Heart of the Mountain Level:** {hotm_level}\n"
                        f"**Mithril Powder:** {format_large_number(mithril_powder)}\n"
                        f"**Gemstone Powder:** {format_large_number(gemstone_powder)}"
                    ),
                    inline=False
                )

                # Price and payment method
                embed.add_field(
                    name="<:money:1291077341950509167> **Price**",
                    value=f"{price} USD",
                    inline=True
                )
                embed.add_field(
                    name="<:PaypalLogo:1291077487207383061> **Payment Methods**",
                    value=payment_method,
                    inline=False
                )

                # Create the additional info embed
                additional_embed = discord.Embed(
                    title="Additional Information",
                    description=additional_info if additional_info else "No additional information provided.",
                    color=discord.Color.blue()
                )
                additional_embed.add_field(
                    name="Listed By",
                    value=f"<@{owner_id}>",
                    inline=False
                )
                additional_embed.set_footer(
                    text="Made By airsbw | https://blazecoins.net",
                    icon_url="https://images-ext-1.discordapp.net/external/p4mQq0j6A_tLFlpktZMDz8uzhy7ksxUjdTaYw-vVnc0/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/463798421074214914/424f24568e095f05ca84a02c3c75aaae.png"
                )

                # Create the new channel in the specified category
                channel = await ctx.guild.create_text_channel(name=channel_name, category=category)

                # Create the view (with buttons)
                view = ListViews()

                # Send embeds in the new channel with the views (buttons)
                await channel.send(embed=embed)
                await channel.send(embed=additional_embed, view=view)

                # Restrict permissions
                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = False
                overwrite.add_reactions = False
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

            await ctx.respond(f"Restored {len(accounts)} accounts.", ephemeral=True)
        else:
            # Deny access if the user doesn't have the required role
            await ctx.respond("You are not allowed to use this command.", ephemeral=True)

def setup(bot):
    bot.add_cog(RestoreCog(bot))
