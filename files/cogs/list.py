import discord
from discord.ext import commands
from discord import Option
from utils.listManage import list_setup  # Import the listManage utility function
from skyblock.fetch_profiles import fetch_profiles  # Import the profile fetching utility
import logging
import json

# Load the config file
with open('config.json') as config_file:
    config = json.load(config_file)
    ACCESS_ROLE_ID = config["access_role"]  # Fetch the access role ID

class ListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def profile_autocomplete(self, ctx: discord.AutocompleteContext):
        """
        Autocomplete function to fetch Skyblock profiles dynamically.
        """
        api_key = ctx.options.get('api_key')  # You can grab api_key from the options context if provided
        ign = ctx.options.get('ign')  # Similar for the IGN
        
        if api_key and ign:
            profiles_data = await fetch_profiles(ign, api_key)
            
            logging.info(f"Fetched profiles: {profiles_data}")
            print(f"Fetched profiles: {profiles_data}")

            try:
                profile_names = profiles_data[0]  # Fetch the list of profile names directly
                return profile_names  # Return the list of names for autocomplete
            except (TypeError, IndexError) as e:
                logging.error(f"Error processing profiles: {e}")
                print(f"Error processing profiles: {e}")
                return []  # Return an empty list if there's an error in processing profiles
        return []  # Return an empty list if no profiles are available

    @commands.slash_command(name="list-skyblock")
    async def list_setup_command(self, 
                                 ctx, 
                                 price: int, 
                                 ign: str, 
                                 api_key: str, 
                                 payment_method: str, 
                                 additional_info: str = None, 
                                 profile: Option(str, "Select a profile", autocomplete=profile_autocomplete) = None):
        """
        Command to create a listing using the listManage utility function with profile autocompletion.
        """
        # Fetch the access role ID from the config
        access_role = discord.utils.get(ctx.guild.roles, id=ACCESS_ROLE_ID)

        # Check if the user has the access role
        if access_role in ctx.author.roles:
            # Defer the response to show the "Thinking..." message
            await ctx.defer(ephemeral=False)
            
            try:
                # Call the list_setup utility function to handle listing creation
                channel = await list_setup(ctx, price, ign, api_key, payment_method, additional_info, profile)

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
    bot.add_cog(ListCog(bot))
