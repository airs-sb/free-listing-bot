import discord
from discord.commands import slash_command
from discord.ext import commands
import json
from utils.database import init_db

conn, c = init_db()

class CreditManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_credits(self, user_id):
        """Load credits from the database"""
        c.execute('SELECT credits FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        if result:
            return result[0]
        return 0  # Default to 0 credits if not found

    def update_credits(self, user_id, credits):
        """Update credits in the database"""
        c.execute('INSERT OR REPLACE INTO users (user_id, credits) VALUES (?, ?)', (user_id, credits))
        conn.commit()

    def is_owner(self, user_id):
        """Check if the user is the owner"""
        with open("config.json") as config_file:
            config = json.load(config_file)
        return int(user_id) == int(config["owner_id"])


    @slash_command(name="credit-add", description="Add credits to a user")
    async def credit_add(self, ctx, user: discord.User, amount: int):
        # Check if the author is the owner
        if not self.is_owner(ctx.author.id):
            embed = discord.Embed(title="Permission Denied", description="You are not allowed to use this command.", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Add credits to the user
        current_credits = self.load_credits(user.id)
        new_credits = current_credits + amount
        self.update_credits(user.id, new_credits)

        embed = discord.Embed(
            title="Credits Added",
            description=f"Added {amount} credits to {user.mention}. They now have {new_credits} credits.",
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(name="credit-remove", description="Remove credits from a user")
    async def credit_remove(self, ctx, user: discord.User, amount: int):
        # Check if the author is the owner
        if not self.is_owner(ctx.author.id):
            embed = discord.Embed(title="Permission Denied", description="You are not allowed to use this command.", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Remove credits from the user
        current_credits = self.load_credits(user.id)
        new_credits = max(0, current_credits - amount)  # Ensure credits don't go negative
        self.update_credits(user.id, new_credits)

        embed = discord.Embed(
            title="Credits Removed",
            description=f"Removed {amount} credits from {user.mention}. They now have {new_credits} credits.",
            color=discord.Color.orange()
        )
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(CreditManagement(bot))
