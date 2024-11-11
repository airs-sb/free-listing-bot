import discord
from discord.ext import commands
from discord import Option
from utils.bedwarsManage import list_bedwars_account  # Import the Bedwars listing utility function
import logging
import json

# Load the config file
with open('config.json') as config_file:
    config = json.load(config_file)
    ACCESS_ROLE_ID = config["access_role"]  # Fetch the access role ID

class ListBedwarsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="list-bedwars")
    async def list_bedwars_command(self, 
                                   ctx, 
                                   price: int, 
                                   ign: str, 
                                   api_key: str, 
                                   payment_method: str, 
                                   additional_info: str = None):
        """
        Command to create a listing for a Bedwars account using the list_bedwars_account function.
        """
        # Fetch the access role ID from the config
        access_role = discord.utils.get(ctx.guild.roles, id=ACCESS_ROLE_ID)

        # Check if the user has the access role
        if access_role in ctx.author.roles:
            # Defer the response to show the "Thinking..." message
            await ctx.defer(ephemeral=False)
            
            try:
                # Call the list_bedwars_account utility function to handle listing creation
                channel = await list_bedwars_account(ctx, price, ign, api_key, payment_method, additional_info)

                # Success embed
                embed = discord.Embed(
                    title="Success",
                    description=f"Your listing has been created in {channel.mention}.",
                    color=discord.Color.green()
                )

                # Edit the original "Thinking..." response with the success embed
                await ctx.interaction.edit_original_response(embed=embed)

            except Exception as e:
                # If an error occurs, respond with an error message
                await ctx.interaction.edit_original_response(content=f"An error occurred: {e}")
        else:
            # Failure message if the user doesn't have the required role
            await ctx.respond("You are not allowed to use this command.", ephemeral=True)

def setup(bot):
    bot.add_cog(ListBedwarsCog(bot))
