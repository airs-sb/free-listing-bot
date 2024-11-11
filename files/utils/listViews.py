# Import required modules
import discord
import json
from utils.database import remove_account
from discord.ext import commands

# Load config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Modal class for payment method input
class PaymentModal(discord.ui.Modal):
    def __init__(self, buyer, interaction):
        super().__init__(title="Payment Method")
        self.buyer = buyer
        self.interaction = interaction

        # Add a text input field for payment method
        self.payment_method = discord.ui.InputText(
            label="Enter Payment Method",
            placeholder="e.g., PayPal, Bank Transfer, etc.",
            style=discord.InputTextStyle.short,
            required=True
        )
        self.add_item(self.payment_method)

    # Use the callback method to handle modal submission
    async def callback(self, interaction: discord.Interaction):
        # After submission, create the private ticket channel and send the message
        guild = self.interaction.guild

        # Retrieve the access_role and buy_accounts_category from config.json
        access_role_id = config["access_role"]
        buy_accounts_category_id = config["buy_accounts_category"]
        account_ping = config["non_role"]

        # Fetch the role and category from the guild
        access_role = guild.get_role(int(access_role_id))
        category = discord.utils.get(guild.categories, id=int(buy_accounts_category_id))

        if not category:
            await interaction.response.send_message("The buy accounts category was not found.", ephemeral=True)
            return

        # Create a private channel in the buy accounts category
        buyer = self.buyer
        channel_name = f"{buyer.name}-buy-ticket"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            buyer: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            access_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        new_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        # Build the message and embed
        embed = discord.Embed(
            title="Buy Account",
            description=f"{buyer.mention} wants to buy {self.interaction.channel.mention}",
            color=discord.Color.brand_red()
        )
        embed.add_field(name="Payment Method", value=self.payment_method.value, inline=False)
        
        # Create the view with the "Close" button
        close_view = CloseTicketView()

        # Send the message to the newly created channel with the "Close" button
        await new_channel.send(f"<@&{access_role_id}>", embed=embed, view=close_view)

        # Respond to the modal interaction
        await interaction.response.send_message(f"Your private channel has been created: {new_channel.mention}", ephemeral=True)

# View for closing the ticket
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout for the view
    
    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # When the button is clicked, delete the channel
        await interaction.channel.delete()

# View for all buttons on the listing message
class ListViews(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent views should have no timeout
    
    # Buy Account Button
    @discord.ui.button(label="Buy Account", style=discord.ButtonStyle.primary, emoji="💵", custom_id="buy_button")
    async def buy_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        buyer = interaction.user
        # Open the payment method modal
        modal = PaymentModal(buyer, interaction)
        await interaction.response.send_modal(modal)

    # Toggle Account Ping Button
    @discord.ui.button(label="Toggle Account Ping", style=discord.ButtonStyle.green, emoji="🔔", custom_id="account_ping_button")
    async def account_ping_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Fetch the role ID from the config
        account_ping_role_id = config["non_role"]

        # Get the role object from the guild
        account_ping_role = interaction.guild.get_role(int(account_ping_role_id))

        if not account_ping_role:
            await interaction.response.send_message("The account ping role was not found.", ephemeral=True)
            return

        # Check if the user already has the role
        if account_ping_role in interaction.user.roles:
            # User has the role, remove it
            await interaction.user.remove_roles(account_ping_role)
            await interaction.response.send_message(f"Removed the `{account_ping_role.name}` role from you.", ephemeral=True)
        else:
            # User doesn't have the role, add it
            await interaction.user.add_roles(account_ping_role)
            await interaction.response.send_message(f"Gave you the `{account_ping_role.name}` role.", ephemeral=True)

    # Unlist Button (No emoji)
    @discord.ui.button(label="Unlist", style=discord.ButtonStyle.danger, emoji="❌", custom_id="unlist_button")
    async def unlist_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Fetch the access role ID from the config and get the role object
        access_role_id = config["access_role"]
        access_role = interaction.guild.get_role(int(access_role_id))

        # Check if the user has the access role
        if access_role in interaction.user.roles:
            # User has the access role, proceed with unlisting
            await interaction.channel.delete()

            # Remove account from the database by channel ID
            remove_account(interaction.channel.id)

            await interaction.response.send_message("Account unlisted and channel deleted.", ephemeral=True)
        else:
            # User does not have the access role
            await interaction.response.send_message("You do not have permission to use this button.", ephemeral=True)


# Function to send message with views
async def send_listing_message(ctx, skyblock_embed, additional_embed):
    view = ListViews()  # Create a new instance of the view

    # Send the embeds with the view (buttons)
    await ctx.send(embed=skyblock_embed, view=view)
    await ctx.send(embed=additional_embed)

    return view  # Returning the view for further processing if necessary

# Make views persistent on restart
def setup(bot: commands.Bot):
    bot.add_view(ListViews())  # Register the view with the bot to make it persistent
