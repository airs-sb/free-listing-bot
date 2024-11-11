import discord
from discord.ext import commands
import sqlite3
from cogs.address import has_access_role

# Initialize the SQLite database
conn = sqlite3.connect("shares.db")
cursor = conn.cursor()

# Create the shares and settings table to store data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS shares (
        id INTEGER PRIMARY KEY,
        user_id TEXT NOT NULL,
        total_sale REAL DEFAULT 0,
        total_share REAL DEFAULT 0
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        rate REAL DEFAULT 0.05
    )
''')
conn.commit()

# Helper function to get the current rate
def get_current_rate():
    cursor.execute("SELECT rate FROM settings WHERE id = 1")
    rate = cursor.fetchone()
    if rate is None:
        cursor.execute("INSERT INTO settings (id, rate) VALUES (1, 0.05)")  # Default to 5% if not set
        conn.commit()
        return 0.05
    return rate[0]

# Helper function to set the rate
def set_rate(new_rate):
    cursor.execute("UPDATE settings SET rate = ? WHERE id = 1", (new_rate,))
    conn.commit()

# Helper function to update or add a sale for a user
def update_sale(user_id, sale_amount):
    rate = get_current_rate()
    share_amount = sale_amount * rate
    
    cursor.execute("SELECT user_id FROM shares WHERE user_id = ?", (user_id,))
    seller = cursor.fetchone()
    
    if seller:
        cursor.execute("UPDATE shares SET total_sale = total_sale + ?, total_share = total_share + ? WHERE user_id = ?",
                       (sale_amount, share_amount, user_id))
    else:
        cursor.execute("INSERT INTO shares (user_id, total_sale, total_share) VALUES (?, ?, ?)",
                       (user_id, sale_amount, share_amount))
    conn.commit()

# Helper function to clear all shares
def clear_all_shares():
    cursor.execute("DELETE FROM shares")
    conn.commit()

# Helper function to clear a specific seller's share
def clear_seller_share(user_id):
    cursor.execute("DELETE FROM shares WHERE user_id = ?", (user_id,))
    conn.commit()

# Helper function to get all sellers' shares
def get_all_shares():
    cursor.execute("SELECT user_id, total_sale, total_share FROM shares")
    return cursor.fetchall()

# Helper function to get a specific seller's share
def get_seller_share(user_id):
    cursor.execute("SELECT total_sale, total_share FROM shares WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

class SharesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Create a slash command group for all share commands
    share = discord.SlashCommandGroup("share", "Commands to manage seller shares and tax.")

    # /share manual-add
    @share.command(name="manual-add", description="Manually add a sale for a seller and calculate their share.")
    @has_access_role()
    async def share_add(self, ctx: discord.ApplicationContext, user: discord.User, amount: float):
        update_sale(user.id, amount)
        embed = discord.Embed(
            title="Sale Added",
            description=f"Added a sale of **${amount:.2f}** for **{user.name}**. Their share has been updated.",
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)

    # /share get
    @share.command(name="get", description="Get the share amount for a specific user.")
    @has_access_role()
    async def share_get(self, ctx: discord.ApplicationContext, user: discord.User):
        share = get_seller_share(user.id)
        if share:
            total_sale, total_share = share
            embed = discord.Embed(
                title=f"Share Details for {user.name}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Total Sales", value=f"${total_sale:.2f}", inline=False)
            embed.add_field(name="Total Share Owed", value=f"${total_share:.2f}", inline=False)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="No Sales Found",
                description=f"{user.name} has no recorded sales.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)

    # /share get-all
    @share.command(name="get-all", description="Get all sellers' shares.")
    @has_access_role()
    async def share_get_all(self, ctx: discord.ApplicationContext):
        shares = get_all_shares()
        if not shares:
            embed = discord.Embed(
                title="No Sales Data",
                description="No sales data available.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)
            return

        description = ""
        for user_id, total_sale, total_share in shares:
            user = await self.bot.fetch_user(user_id)
            description += f"<@{user.id}> | **${total_share:.2f}**\n"

        embed = discord.Embed(
            title="Seller Shares",
            description=description,
            color=discord.Color.blue()
        )

        await ctx.respond(embed=embed)


    # /share clear-all
    @share.command(name="clear-all", description="Clear all sellers' shares.")
    @has_access_role()
    async def share_clear_all(self, ctx: discord.ApplicationContext):
        clear_all_shares()
        embed = discord.Embed(
            title="All Shares Cleared",
            description="All sellers' shares have been cleared.",
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)

    # /share clear-seller
    @share.command(name="clear-seller", description="Clear a specific seller's share (mark as paid).")
    @has_access_role()
    async def share_clear_seller(self, ctx: discord.ApplicationContext, user: discord.User):
        clear_seller_share(user.id)
        embed = discord.Embed(
            title="Seller Share Cleared",
            description=f"{user.name}'s share has been cleared (marked as paid).",
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)

    # /share setup (set the rate)
    @share.command(name="setup", description="Set the share rate (e.g., 5 for 5%).")
    @has_access_role()
    async def share_setup(self, ctx: discord.ApplicationContext, rate: float):
        new_rate = rate / 100  # Convert percentage to decimal
        set_rate(new_rate)
        embed = discord.Embed(
            title="Share Rate Updated",
            description=f"Share rate set to **{rate}%**.",
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)

    # /share get-own (get your own share amount)
    @share.command(name="get-own", description="Get your own share amount.")
    @has_access_role()
    async def share_get_own(self, ctx: discord.ApplicationContext):
        share = get_seller_share(ctx.author.id)
        if share:
            total_sale, total_share = share
            embed = discord.Embed(
                title="Share Amount",
                description=f"You owe a total of ${total_share:.1f}",
                color=discord.Color.blue()
            )
            # embed.add_field(name="Total Sales", value=f"${total_sale:.2f}", inline=False)
            # embed.add_field(name="Total Share Owed", value=f"${total_share:.2f}", inline=False)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="No Sales Found",
                description="You have no recorded sales.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)

    # Command to log a sale for the logged-in user
    @commands.slash_command(name="log", description="Log a sale for yourself.")
    @has_access_role()
    async def log_sale(self, ctx: discord.ApplicationContext, amount: float):
        update_sale(ctx.author.id, amount)
        embed = discord.Embed(
            title="Sale Logged",
            description=f"Logged a sale of **${amount:.2f}** for yourself.",
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(SharesCog(bot))
