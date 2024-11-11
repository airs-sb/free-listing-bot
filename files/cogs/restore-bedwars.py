import discord
from discord.ext import commands
from utils.bedwars_database import fetch_all_bedwars_accounts
from utils.listViews import ListViews  # Import the views from your current setup
import json

# Load config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)
    ACCESS_ROLE_ID = config["access_role"]  # Fetch the access role ID
    

class RestoreBedwarsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="restore-bedwars")
    async def restore_bedwars_accounts(self, ctx):
        """
        Command to restore all the listed Bedwars accounts and recreate their channels and embeds.
        """

        # Fetch the access role from the config
        access_role = discord.utils.get(ctx.guild.roles, id=ACCESS_ROLE_ID)

        # Check if the user has the access role
        if access_role in ctx.author.roles:
            # Proceed if the user has the required role
        

            accounts = fetch_all_bedwars_accounts()

            # Retrieve the accounts category from the guild using the category ID from config
            category_id = config["bedwars_category"]
            category = discord.utils.get(ctx.guild.categories, id=int(category_id))

            if category is None:
                await ctx.respond("Category not found! Please ensure the category ID is correct in config.json.", ephemeral=True)
                return

            for account in accounts:
                (owner_id, price, ign, api_key, payment_method, additional_info, channel_id, channel_name,
                rank, stars, wins, losses, kills, deaths, final_kills, final_deaths, beds_broken, beds_lost, games_played) = account[1:]

                # Create the Bedwars stats embed
                embed = discord.Embed(
                    title=f"Bedwars Stats",
                    color=discord.Color.blue()  # Matching color
                )
                
                # Add fields using the style of the example you provided
                embed.add_field(
                    name="<:5526bluestar:1291711175557513332> Overall Stats",
                    value=(
                        f"**Rank:** {rank}\n"
                        f"**Stars:** {stars}\n"
                        f"**Wins:** {wins:,}\n"
                    ),
                    inline=True
                )
                
                embed.add_field(
                    name="<:final_death:1291711325117878365> Kills / Deaths",
                    value=(
                        f"**Kills:** {kills:,}\n"
                        f"**Deaths:** {deaths:,}\n"
                        f"**Final Kills:** {final_kills:,}\n"
                        f"**Final Deaths:** {final_deaths:,}\n"
                    ),
                    inline=False
                )

                embed.add_field(
                    name="<:1236755172139728997:1289571625666347110> Other Stats",
                    value=(
                        f"**Losses:** {losses:,}\n"
                        f"**Beds Broken:** {beds_broken:,}\n"
                        f"**Beds Lost:** {beds_lost:,}\n"
                        f"**Games Played:** {games_played:,}\n"
                    ),
                    inline=False
                )
                
                # Price and payment method
                embed.add_field(
                    name="<:money:1291077341950509167> Price",
                    value=f"{price} USD",
                    inline=False
                )
                embed.add_field(
                    name="<:PaypalLogo:1291077487207383061> Payment Method",
                    value=payment_method,
                    inline=False
                )
                
                embed.set_thumbnail(url="https://mc-heads.net/body/Anonymous/left")  # Consistent thumbnail
                
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
    bot.add_cog(RestoreBedwarsCog(bot))
