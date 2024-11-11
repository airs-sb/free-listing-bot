import discord
from discord.ext import commands
import sqlite3
from cogs.address import has_access_role

# Initialize the SQLite database
conn = sqlite3.connect("tags.db")
cursor = conn.cursor()

# Create the tags table to store the tags
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        value TEXT NOT NULL,
        tag_type TEXT NOT NULL,  -- 'user' for public or 'personal' for personal tags
        user_id TEXT  -- Stores the user ID if the tag is personal
    )
''')
conn.commit()

class TagsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to add a tag
    @commands.slash_command(name="tag-add", description="Add a new tag")
    @has_access_role()
    async def tag_add(self, ctx: discord.ApplicationContext, name: str, value: str, tag_type: discord.Option(str, choices=["user", "personal"])):
        # Check if the tag already exists
        cursor.execute("SELECT name FROM tags WHERE name = ? AND (tag_type = 'user' OR (tag_type = 'personal' AND user_id = ?))", (name, str(ctx.author.id)))
        existing_tag = cursor.fetchone()

        if existing_tag:
            await ctx.respond(f"A tag with the name `{name}` already exists.", ephemeral=True)
            return

        # Add the tag to the database
        cursor.execute("INSERT INTO tags (name, value, tag_type, user_id) VALUES (?, ?, ?, ?)",
                       (name, value, tag_type, str(ctx.author.id) if tag_type == "personal" else None))
        conn.commit()

        await ctx.respond(f"Tag `{name}` added successfully.", ephemeral=True)

    # Command to remove a tag
    @commands.slash_command(name="tag-remove", description="Remove a tag")
    @has_access_role()
    async def tag_remove(self, ctx: discord.ApplicationContext, name: str):
        # Check if the tag exists and the user has permission to remove it (personal tag or public)
        cursor.execute("SELECT name FROM tags WHERE name = ? AND (tag_type = 'user' OR (tag_type = 'personal' AND user_id = ?))", (name, str(ctx.author.id)))
        tag = cursor.fetchone()

        if not tag:
            await ctx.respond(f"Tag `{name}` not found or you do not have permission to remove it.", ephemeral=True)
            return

        # Remove the tag from the database
        cursor.execute("DELETE FROM tags WHERE name = ? AND (tag_type = 'user' OR (tag_type = 'personal' AND user_id = ?))", (name, str(ctx.author.id)))
        conn.commit()

        await ctx.respond(f"Tag `{name}` removed successfully.", ephemeral=True)

    # Listen for any message and check if it matches any tag
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return  # Ignore bot messages

        # Check for a matching public tag
        cursor.execute("SELECT value FROM tags WHERE name = ? AND tag_type = 'user'", (message.content,))
        tag = cursor.fetchone()

        # If no public tag is found, check for personal tags
        if not tag:
            cursor.execute("SELECT value FROM tags WHERE name = ? AND tag_type = 'personal' AND user_id = ?", (message.content, str(message.author.id)))
            tag = cursor.fetchone()

        # If a tag is found, send the tag's value as a message
        if tag:
            await message.channel.send(tag[0])

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(TagsCog(bot))
