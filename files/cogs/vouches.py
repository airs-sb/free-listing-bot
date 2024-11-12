import discord
from discord.ext import commands
import json
import os
import datetime

# Path to store message data in vouches.json
MESSAGE_FILE_PATH = './vouches.json'

# Ensure the vouches.json file exists
if not os.path.exists(MESSAGE_FILE_PATH):
    with open(MESSAGE_FILE_PATH, 'w') as f:
        json.dump({}, f)  # Start with an empty dictionary

class MessageStoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Utility function to load messages from vouches.json
    def load_messages(self):
        with open(MESSAGE_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Utility function to save messages to vouches.json
    def save_messages(self, data):
        with open(MESSAGE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Slash command to store all messages in the channel
    @commands.slash_command(name="store", description="Stores all messages sent in the channel.")
    async def store_messages(self, ctx: discord.ApplicationContext):
        await ctx.defer()  # Defer reply while the command runs

        message_data = self.load_messages()
        channel_id = str(ctx.channel.id)

        if channel_id not in message_data:
            message_data[channel_id] = []

        # Fetch all messages in the channel and store them
        async for message in ctx.channel.history(limit=None):
            if not message.author.bot:
                attachments = [attachment.url for attachment in message.attachments]
                message_data[channel_id].append({
                    "content": message.content,
                    "username": message.author.name,
                    "avatar": str(message.author.display_avatar.url),
                    "attachments": attachments
                })

        self.save_messages(message_data)

        await ctx.followup.send(f"Stored {len(message_data[channel_id])} messages in the channel.")

    # Slash command to restore messages using a specific webhook
    @commands.slash_command(name="restore-vouches", description="Restores stored messages using the provided webhook.")
    async def restore_vouches(self, ctx: discord.ApplicationContext, webhook: str):
        await ctx.defer()  # Defer reply while the command runs

        message_data = self.load_messages()
        channel_id = str(ctx.channel.id)

        if channel_id not in message_data or len(message_data[channel_id]) == 0:
            await ctx.followup.send("No stored messages found for this channel.")
            return

        webhook_url = webhook

        # Restore messages using the provided webhook in reverse order
        for msg in reversed(message_data[channel_id]):
            try:
                # Send message using the provided webhook
                webhook_client = discord.SyncWebhook.from_url(webhook_url)

                # Send message via webhook
                webhook_client.send(
                    content=msg['content'],
                    username=msg['username'],
                    avatar_url=msg['avatar'],
                    files=[discord.File(attachment) for attachment in msg['attachments']]
                )
            except Exception as e:
                print(f"Error restoring message from {msg['username']}: {e}")

        await ctx.followup.send("Messages restored successfully.")

    # Utility method to fetch and download avatars for webhooks
    async def fetch_avatar(self, avatar_url: str):
        async with self.bot.session.get(avatar_url) as response:
            if response.status == 200:
                return await response.read()

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(MessageStoreCog(bot))
