import random
import string
import discord
from discord.commands import slash_command
from discord.ext import commands
from utils.database import init_db
import json

conn, c = init_db()

class KeyManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner(self, user_id):
        """Check if the user is the owner"""
        with open("config.json") as config_file:
            config = json.load(config_file)
        return int(user_id) == int(config["owner_id"])

    def generate_key(self):
        """Generates a random key"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

    def add_key_to_db(self, key, credits):
        """Stores the key and credit value in the database"""
        c.execute('INSERT INTO keys (key, credits, redeemed) VALUES (?, ?, ?)', (key, credits, 0))
        conn.commit()

    def get_key(self, key):
        """Retrieves the key information from the database"""
        c.execute('SELECT * FROM keys WHERE key = ?', (key,))
        return c.fetchone()

    def mark_key_redeemed(self, key):
        """Marks a key as redeemed"""
        c.execute('UPDATE keys SET redeemed = 1 WHERE key = ?', (key,))
        conn.commit()

    def add_credits(self, user_id, credits):
        """Adds credits to a user"""
        c.execute('SELECT credits FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        if result:
            new_credits = result[0] + credits
            c.execute('UPDATE users SET credits = ? WHERE user_id = ?', (new_credits, user_id))
        else:
            c.execute('INSERT INTO users (user_id, credits) VALUES (?, ?)', (user_id, credits))
        conn.commit()

    @slash_command(name="create-key", description="Create keys that grant credits")
    async def create_key(self, ctx, amount: int, credits: int):
        # Only the owner can create keys
        if not self.is_owner(ctx.author.id):
            embed = discord.Embed(title="Permission Denied", description="Only the owner can create keys.", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        keys = []
        for _ in range(amount):
            key = self.generate_key()
            self.add_key_to_db(key, credits)
            keys.append(key)
        
        embed = discord.Embed(
            title="Keys Created",
            description=f"Created {amount} keys, each granting {credits} credits.",
            color=discord.Color.green()
        )
        embed.add_field(name="Keys", value='\n'.join(keys), inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(name="redeem", description="Redeem a key for credits")
    async def redeem_key(self, ctx, key: str):
        # Check if the key exists and is not redeemed
        key_data = self.get_key(key)
        if not key_data:
            embed = discord.Embed(title="Invalid Key", description="The key you entered is invalid.", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if key_data[2]:  # Check if the key is already redeemed
            embed = discord.Embed(title="Key Already Redeemed", description="This key has already been redeemed.", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Add credits to the user
        credits = key_data[1]
        self.add_credits(ctx.author.id, credits)
        self.mark_key_redeemed(key)

        embed = discord.Embed(
            title="Key Redeemed",
            description=f"You have redeemed the key and received {credits} credits.",
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(KeyManager(bot))
