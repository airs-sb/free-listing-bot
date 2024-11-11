import discord
from discord.ext import commands
import sqlite3
import json
from discord.commands import SlashCommandGroup
from cogs.address import has_access_role


# Load config.json for base prices
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Ensure the base prices are converted to floats
coin_price_buy = float(config.get("coin_price_buy", 0.04))  # Default price per million coins
coin_price_sell = float(config.get("coin_price_sell", 0.035))  # Default price per million coins

# Initialize the SQLite database
conn = sqlite3.connect("coins.db")
cursor = conn.cursor()

# Create tables for dynamic pricing and transactions
cursor.execute('''CREATE TABLE IF NOT EXISTS dynamic_prices (
                    id INTEGER PRIMARY KEY,
                    transaction_type TEXT,
                    price REAL,
                    amount REAL
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT,
                    transaction_type TEXT,
                    amount REAL,
                    price_per_m REAL,
                    total_price REAL,
                    payment_method TEXT
                )''')

conn.commit()

# Load dynamic pricing from the database
def load_dynamic_prices(transaction_type):
    cursor.execute("SELECT price, amount FROM dynamic_prices WHERE transaction_type = ?", (transaction_type,))
    return cursor.fetchall()

# Save dynamic pricing into the database
def save_dynamic_price(transaction_type, price, amount):
    cursor.execute("INSERT INTO dynamic_prices (transaction_type, price, amount) VALUES (?, ?, ?)", (transaction_type, price, amount))
    conn.commit()

# Remove dynamic pricing from the database
def remove_dynamic_price(transaction_type, price, amount):
    cursor.execute("DELETE FROM dynamic_prices WHERE transaction_type = ? AND price = ? AND amount = ?", (transaction_type, price, amount))
    conn.commit()

# Save a transaction in the database
def save_transaction(user_id, transaction_type, amount, price_per_m, total_price, payment_method):
    cursor.execute("INSERT INTO transactions (user_id, transaction_type, amount, price_per_m, total_price, payment_method) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, transaction_type, amount, price_per_m, total_price, payment_method))
    conn.commit()

# Number parser to handle 'k', 'm', 'b', 't' inputs
def parse_number(input_str):
    multipliers = {
        'k': 1_000,        # thousand
        'm': 1_000_000,    # million
        'b': 1_000_000_000, # billion
        't': 1_000_000_000_000 # trillion
    }
    
    try:
        if input_str[-1].lower() in multipliers:
            return float(input_str[:-1]) * multipliers[input_str[-1].lower()]
        else:
            return float(input_str)  # No multiplier, treat as plain number
    except ValueError:
        raise ValueError("Invalid number format. Use digits with 'k', 'm', 'b', 't' or plain numbers.")

# Format large numbers into readable strings (e.g., 1 million = "1M")
def format_large_number(number):
    if number >= 1_000_000_000_000:
        return f"{number / 1_000_000_000_000:.2f}T"
    elif number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.2f}K"
    else:
        return str(int(number))

# Calculate the price for the given amount based on dynamic price tiers
def calculate_dynamic_price(amount, price_tiers, base_price):
    sorted_tiers = sorted(price_tiers, key=lambda x: x[1], reverse=True)  # Sort tiers in descending order
    for tier in sorted_tiers:
        if amount >= tier[1]:  # Check if the amount is greater than the tier threshold
            return tier[0]
    return base_price  # If no tier matches, return base price

class CloseTicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_button")
    async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            # Close the ticket by deleting the channel
            channel = interaction.channel
            await channel.delete(reason="Ticket closed by user.")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while closing the ticket: {e}.", ephemeral=True)

class CoinsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Create a Slash Command Group for dnc
    dnc = SlashCommandGroup(name="dnc", description="Manage dynamic coin pricing tiers")

    # Command to dynamically add a buy price tier
    @dnc.command(name="add-buy", description="Add a dynamic coin pricing tier for buying coins")
    @has_access_role()
    async def dnc_add_buy(self, ctx, price: float, amount: str):
        try:
            amount_in_b = parse_number(amount)  # Parse the amount input (convert to number)

            # Add the new tier to the database
            save_dynamic_price('buy', price, amount_in_b)

            # Confirm to the user
            await ctx.respond(f"Added buy price tier: {price}/m for amounts above {format_large_number(amount_in_b)}.")
        except ValueError as e:
            await ctx.respond(f"Error: {str(e)}", ephemeral=True)

    # Command to dynamically remove a buy price tier
    @dnc.command(name="remove-buy", description="Remove a dynamic coin pricing tier for buying coins")
    @has_access_role()
    async def dnc_remove_buy(self, ctx, price: float, amount: str):
        try:
            amount_in_b = parse_number(amount)  # Parse the amount input (convert to number)

            # Remove the tier from the database
            remove_dynamic_price('buy', price, amount_in_b)

            # Confirm to the user
            await ctx.respond(f"Removed buy price tier: {price}/m for amounts above {format_large_number(amount_in_b)}.")
        except ValueError as e:
            await ctx.respond(f"Error: {str(e)}", ephemeral=True)

    # Command to dynamically add a sell price tier
    @dnc.command(name="add-sell", description="Add a dynamic coin pricing tier for selling coins")
    @has_access_role()
    async def dnc_add_sell(self, ctx, price: float, amount: str):
        try:
            amount_in_b = parse_number(amount)  # Parse the amount input (convert to number)

            # Add the new tier to the database
            save_dynamic_price('sell', price, amount_in_b)

            # Confirm to the user
            await ctx.respond(f"Added sell price tier: {price}/m for amounts above {format_large_number(amount_in_b)}.")
        except ValueError as e:
            await ctx.respond(f"Error: {str(e)}", ephemeral=True)

    # Command to dynamically remove a sell price tier
    @dnc.command(name="remove-sell", description="Remove a dynamic coin pricing tier for selling coins")
    @has_access_role()
    async def dnc_remove_sell(self, ctx, price: float, amount: str):
        try:
            amount_in_b = parse_number(amount)  # Parse the amount input (convert to number)

            # Remove the tier from the database
            remove_dynamic_price('sell', price, amount_in_b)

            # Confirm to the user
            await ctx.respond(f"Removed sell price tier: {price}/m for amounts above {format_large_number(amount_in_b)}.")
        except ValueError as e:
            await ctx.respond(f"Error: {str(e)}", ephemeral=True)

    # Modal for collecting payment method and amount
    class CoinTransactionModal(discord.ui.Modal):
        def __init__(self, transaction_type):
            self.transaction_type = transaction_type  # 'buy' or 'sell'
            super().__init__(title=f"{transaction_type.capitalize()} Coins")

            self.add_item(discord.ui.InputText(label="Amount", placeholder="Enter the amount (e.g., 1k, 1m, etc.)", required=True))
            self.add_item(discord.ui.InputText(label="Payment Method", placeholder="Enter your payment method", required=True))

        async def callback(self, interaction: discord.Interaction):
            try:
                # Retrieve input values
                raw_amount = self.children[0].value
                payment_method = self.children[1].value

                # Parse the amount using the number parser (amount is in coins)
                amount = parse_number(raw_amount)
                millions_of_coins = amount / 1_000_000  # Convert to millions of coins

                # Load dynamic price tiers from the database
                buy_prices = load_dynamic_prices('buy')
                sell_prices = load_dynamic_prices('sell')

                # Calculate total price based on millions of coins
                if self.transaction_type == "buy":
                    price_per_million = calculate_dynamic_price(amount, buy_prices, coin_price_buy)
                else:
                    price_per_million = calculate_dynamic_price(amount, sell_prices, coin_price_sell)

                total_price = millions_of_coins * price_per_million

                # Save the transaction to the database
                save_transaction(interaction.user.id, self.transaction_type, amount, price_per_million, total_price, payment_method)

                # Create a ticket channel
                guild = interaction.guild
                transaction_type = "buy" if self.transaction_type == "buy" else "sell"
                ticket_channel_name = f"{transaction_type}-coins-{interaction.user.name}"
                ticket_channel = await guild.create_text_channel(name=ticket_channel_name)

                # Set permissions for the ticket channel (private between the user and the bot)
                overwrite = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                }
                await ticket_channel.edit(overwrites=overwrite)

                # Format the amount and total price for readability
                formatted_amount = format_large_number(amount)
                formatted_price = f"${total_price:.2f}"

                # Create the ticket embed
                ticket_embed = discord.Embed(
                    title=f"{transaction_type.capitalize()} Coins Ticket",
                    description=f"Transaction details for {transaction_type.capitalize()}ing coins",
                    color=discord.Color.blue()
                )
                ticket_embed.add_field(name="Amount", value=f"{raw_amount} ({formatted_amount} coins)", inline=False)
                ticket_embed.add_field(name="Total Price", value=formatted_price, inline=False)
                ticket_embed.add_field(name="Payment Method", value=payment_method, inline=False)
                ticket_embed.set_footer(text="Click the button below to close the ticket.")

                # Send the embed with a close ticket button
                view = CloseTicketButton()
                await ticket_channel.send(embed=ticket_embed, view=view)

                # Confirm ticket creation to the user
                await interaction.response.send_message(f"Ticket created successfully! Check {ticket_channel.mention}.", ephemeral=True)

            except ValueError as e:
                await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {e}.", ephemeral=True)

    # Button view for buying and selling coins
    class CoinTransactionButton(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Buy Coins", style=discord.ButtonStyle.primary, custom_id="buy_coins_button", emoji="<:1236756044588253184:1289571640702926878>")
        async def buy_coins(self, button: discord.ui.Button, interaction: discord.Interaction):
            # Show the modal for buying coins
            modal = CoinsCog.CoinTransactionModal(transaction_type="buy")
            await interaction.response.send_modal(modal)

        @discord.ui.button(label="Sell Coins", style=discord.ButtonStyle.primary, custom_id="sell_coins_button", emoji="<:1236756044588253184:1289571640702926878>")
        async def sell_coins(self, button: discord.ui.Button, interaction: discord.Interaction):
            # Show the modal for selling coins
            modal = CoinsCog.CoinTransactionModal(transaction_type="sell")
            await interaction.response.send_modal(modal)

    # Create a Slash Command Group for ticket panel
    ticket_panel = SlashCommandGroup(name="ticket-panel", description="Manage ticket panels")

    @ticket_panel.command(name="coins", description="Display the coin prices and options to buy or sell coins")
    @has_access_role()
    async def coins(self, ctx: discord.ApplicationContext):
        try:
            # Load dynamic pricing from the database
            dnc_buy_prices = load_dynamic_prices('buy')
            dnc_sell_prices = load_dynamic_prices('sell')

            # Create an embed with the current coin prices and dynamic tiers
            buy_field = f"**250M-500M** `0.045/m`\n"
            sell_field = f"**All Amounts** `0.02/m`\n"

            # Add the dynamic tiers to the buy and sell fields
            for tier in sorted(dnc_buy_prices, key=lambda x: x[1]):
                buy_field += f"`{tier[0]:.3f}/m` above {format_large_number(tier[1])}\n"

            for tier in sorted(dnc_sell_prices, key=lambda x: x[1]):
                sell_field += f"`{tier[0]:.3f}/m` above {format_large_number(tier[1])}\n"

            embed = discord.Embed(
                title="Shady Coins",
                description="",
                color=discord.Color(0x2F3136)
            )

            # Add the fields to the embed
            embed.add_field(name="<:coin:1291711299511910450> Buy Coins", value=buy_field, inline=True)
            embed.add_field(name="<:coin:1291711299511910450> Sell Coins", value=sell_field, inline=True)

            # Send the embed with the buy/sell buttons
            view = CoinsCog.CoinTransactionButton()
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            # Notify the user about the error
            await ctx.send(f"An error occurred: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        # Add persistent view when the bot is ready
        self.bot.add_view(CoinsCog.CoinTransactionButton())  # Add the transaction view for persistent buttons
        self.bot.add_view(CloseTicketButton())  # Add persistent close ticket view
        print("Persistent views added.")

# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(CoinsCog(bot))
