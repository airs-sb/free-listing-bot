import os
import discord
from discord.commands import slash_command
from discord.ext import commands
import json

class EmojiUploader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_manage_emojis(self, member):
        """Check if the user has the 'Manage Emojis' permission."""
        return member.guild_permissions.manage_emojis

    def get_emoji_folder(self):
        """Returns the path to the emoji folder."""
        return './emojis/'

    def load_config(self):
        """Loads the config file."""
        with open("config.json") as config_file:
            return json.load(config_file)

    async def upload_emoji(self, guild, filename):
        """Uploads an emoji to the server."""
        emoji_folder = self.get_emoji_folder()
        emoji_name = os.path.splitext(filename)[0]  # Remove the file extension for emoji name
        file_path = os.path.join(emoji_folder, filename)
        
        try:
            with open(file_path, 'rb') as image:
                emoji = await guild.create_custom_emoji(name=emoji_name, image=image.read())
                return f"Uploaded emoji: {emoji_name} {emoji}"
        except discord.HTTPException as e:
            return f"Failed to upload {emoji_name}: {e}"

    async def delete_emoji(self, emoji):
        """Deletes an emoji from the server."""
        try:
            await emoji.delete()
            return f"Deleted emoji: {emoji.name}"
        except discord.HTTPException as e:
            return f"Failed to delete {emoji.name}: {e}"

    @slash_command(name="emojis", description="Upload all emojis from the emojis folder.")
    async def upload_emojis(self, ctx):
        if not self.has_manage_emojis(ctx.author):
            embed = discord.Embed(title="Permission Denied", description="You don't have permission to manage emojis.", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return

        emoji_folder = self.get_emoji_folder()
        if not os.path.exists(emoji_folder):
            embed = discord.Embed(title="Error", description="Emoji folder not found!", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return

        messages = []
        for filename in os.listdir(emoji_folder):
            if filename.endswith('.png') or filename.endswith('.jpg'):
                message = await self.upload_emoji(ctx.guild, filename)
                messages.append(message)
            else:
                messages.append(f"File {filename} is not a valid image format.")

        embed = discord.Embed(title="Emoji Upload Results", description='\n'.join(messages), color=discord.Color.green())
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(EmojiUploader(bot))
