import discord
from discord.ext import commands
import shutil
import os
import subprocess
import json
from utils.venv import get_venv_python  # Import the venv utility
from cogs.address import has_access_role

class RestartCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="restart", description="Restart the bot with the latest files")
    @has_access_role()  # Ensure the user has the access role
    async def restart(self, ctx: discord.ApplicationContext, venv_name: str):
        # Notify the user that the restart is starting
        await ctx.respond("Restarting the bot with the latest files...", ephemeral=True)

        # Automatically find the main folder based on script location
        current_directory = os.path.dirname(os.path.realpath(__file__))

        # Correct path to the "files" folder (three directories up from 'cogs')
        source_folder = os.path.normpath(os.path.join(current_directory, "..", "..", "..", "files"))

        # The actual destination directory should be one level above the current directory (i.e., the folder above "cogs")
        destination_folder = os.path.normpath(os.path.join(current_directory, ".."))

        # Check if the files folder exists
        if not os.path.exists(source_folder):
            await ctx.respond(f"Error: Could not find the 'files' folder in {source_folder}", ephemeral=True)
            return

        # Remove files in the destination directory that are not in the source_folder, except for database.db and config.json
        keep_files = {"database.db", "config.json", "skyblock_accounts.db", "bedwars_accounts.db", "coins.db", "tags.db", "shares.db", "vouches.json", "addresses.db"}  # Files to keep
        try:
            for item in os.listdir(destination_folder):
                item_path = os.path.join(destination_folder, item)
                if item not in keep_files and not item.startswith("."):  # Avoid hidden files
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        print(f"Removed file: {item_path}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        print(f"Removed directory: {item_path}")
        except Exception as e:
            await ctx.respond(f"Error cleaning destination folder: {e}", ephemeral=True)
            return

        # Copy all files and directories recursively from the "files" folder to the destination directory
        try:
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    # Get the relative path to maintain folder structure
                    relative_path = os.path.relpath(root, source_folder)
                    destination_dir = os.path.join(destination_folder, relative_path)

                    # Ensure the destination directory exists
                    os.makedirs(destination_dir, exist_ok=True)

                    # Source and destination paths for each file
                    source_file = os.path.join(root, file)
                    destination_file = os.path.join(destination_dir, file)

                    # Copy the file
                    shutil.copy2(source_file, destination_file)
                    print(f"Copied file: {source_file} to {destination_file}")
        except Exception as e:
            await ctx.respond(f"Error copying files: {e}", ephemeral=True)
            return

        # Load the token from the config.json file
        config_path = os.path.join(destination_folder, "config.json")
        if not os.path.exists(config_path):
            await ctx.respond(f"Error: Could not find config.json in {config_path}", ephemeral=True)
            return

        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                token = config.get("token")

            if not token:
                await ctx.respond("Error: Could not find token in config.json", ephemeral=True)
                return
        except Exception as e:
            await ctx.respond(f"Error reading config.json: {e}", ephemeral=True)
            return

        # Get the Python executable from the virtual environment
        try:
            venv_python = get_venv_python(venv_name)
        except FileNotFoundError as e:
            await ctx.respond(f"Error: {str(e)}", ephemeral=True)
            return

        # Path to bot.py (in the root directory)
        bot_file = os.path.normpath(os.path.join(destination_folder, "bot.py"))

        if not os.path.exists(bot_file):
            await ctx.respond(f"Error: Could not find bot.py in {destination_folder}", ephemeral=True)
            return

        # Start the bot using subprocess with the venv's python and the token from config.json
        try:
            subprocess.Popen([venv_python, bot_file], cwd=os.path.dirname(bot_file))
            print(f"Started bot with {venv_python} {bot_file}")
        except Exception as e:
            await ctx.respond(f"Error starting the bot: {e}", ephemeral=True)
            return

        # Notify that the bot is restarting and then stop the current bot process
        await ctx.respond("Bot restarted successfully. Stopping the current process...", ephemeral=True)
        await self.bot.close()


# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(RestartCog(bot))
