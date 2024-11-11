import discord
from discord.ext import commands
import sqlite3
import json

# Load the access role ID from config.json
with open('config.json') as f:
    config = json.load(f)
access_role = config["access_role"]

def has_access_role():
    async def predicate(ctx):
        # Check if the user has the required role
        return any(role.id == access_role for role in ctx.author.roles)
    return commands.check(predicate)

class Addresses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Set up the database connection
        self.conn = sqlite3.connect('addresses.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                user_id INTEGER,
                type TEXT,
                value TEXT,
                PRIMARY KEY (user_id, type)
            )
        ''')
        self.conn.commit()

    def cog_unload(self):
        self.conn.close()

    addresses = discord.SlashCommandGroup("addresses", "Manage your addresses")

    @addresses.command()
    @has_access_role()  # Ensure the user has the access role
    async def add(
        self,
        ctx,
        type: discord.Option(str, "Type of address", choices=[
            'cashapp', 'paypal', 'ltc', 'btc', 'eth', 'usdt', 'venmo', 'apple', 'card', 'google'
        ]),
        value: discord.Option(str, "The value of the address")
    ):
        user_id = ctx.author.id
        self.cursor.execute('''
            INSERT OR REPLACE INTO addresses (user_id, type, value)
            VALUES (?, ?, ?)
        ''', (user_id, type, value))
        self.conn.commit()
        await ctx.respond(f"Your {type} address has been set.", ephemeral=True)

    @addresses.command()
    @has_access_role()  # Ensure the user has the access role
    async def get(self, ctx):
        user_id = ctx.author.id
        self.cursor.execute('''
            SELECT type, value FROM addresses WHERE user_id = ?
        ''', (user_id,))
        results = self.cursor.fetchall()
        if not results:
            await ctx.respond("You have not set any addresses.", ephemeral=True)
            return

        address_list = [{'type': row[0], 'value': row[1]} for row in results]
        view = AddressSelectView(address_list, self)
        await ctx.respond("Select an address:", view=view, ephemeral=True)

    @addresses.command()
    @has_access_role()  # Ensure the user has the access role
    async def remove(
        self,
        ctx,
        type: discord.Option(str, "Type of address", choices=[
            'cashapp', 'paypal', 'ltc', 'btc', 'eth', 'usdt', 'venmo', 'apple', 'card', 'google'
        ])
    ):
        user_id = ctx.author.id
        self.cursor.execute('''
            DELETE FROM addresses WHERE user_id = ? AND type = ?
        ''', (user_id, type))
        self.conn.commit()
        await ctx.respond(f"Your {type} address has been removed.", ephemeral=True)

class AddressSelect(discord.ui.Select):
    def __init__(self, addresses, cog):
        self.addresses = addresses  # List of dicts with 'type' and 'value'
        self.cog = cog
        options = []
        for addr in addresses:
            # Truncate label and description if necessary
            label = f"{addr['type'].capitalize()}: {addr['value'][:50]}"
            description = addr['value'][:100]
            # Use a combination of type and a unique identifier as the option value to ensure uniqueness
            option_value = f"{addr['type']}_{addr['value']}"
            options.append(discord.SelectOption(label=label, value=option_value, description=description))
        super().__init__(placeholder="Select an address", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        # Split the option value back into type and value
        selected_type, _ = selected_value.split('_', 1)
        # Retrieve the address value
        self.cog.cursor.execute('''
            SELECT value FROM addresses WHERE user_id = ? AND type = ?
        ''', (interaction.user.id, selected_type))
        result = self.cog.cursor.fetchone()
        if result:
            value = result[0]
            # Send the address publicly in the channel
            await interaction.channel.send(
                f"{interaction.user.mention}'s {selected_type} address is: {value}"
            )
            # Acknowledge the interaction
            await interaction.response.defer()
        else:
            await interaction.response.send_message(
                "Address not found."
            )

class AddressSelectView(discord.ui.View):
    def __init__(self, addresses, cog):
        super().__init__()
        self.cog = cog
        self.add_item(AddressSelect(addresses, cog))

def setup(bot):
    bot.add_cog(Addresses(bot))
