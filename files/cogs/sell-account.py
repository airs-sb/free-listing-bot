import discord
import random
import json
from discord.ext import commands
from utils.skyblock_embed import create_skyblock_embed
from utils.database import insert_account
from cogs.address import has_access_role

# Load config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)


# Modal to collect details for the account listing
class SellAccountModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Sell Account Details")

        # Modal fields
        self.add_item(discord.ui.InputText(label="IGN", placeholder="Enter your in-game name", required=True))
        self.add_item(discord.ui.InputText(label="Offer", placeholder="Enter your offer", required=True))
        self.add_item(discord.ui.InputText(label="Payment Method", placeholder="Enter your payment method", required=True))

    async def callback(self, interaction: discord.Interaction):
        try:
            # Send an ephemeral message indicating the ticket creation is in progress
            await interaction.response.send_message("Making ticket... Please wait.", ephemeral=True)

            print("Modal submitted, starting process...")
            # Retrieve input from modal
            ign = self.children[0].value
            offer = int(self.children[1].value)  # Convert offer to integer
            payment_method = self.children[2].value
            print(f"Received: IGN={ign}, Offer={offer}, Payment Method={payment_method}")

            # Fetch guild info from the interaction context
            guild = interaction.guild
            print(f"Guild fetched: {guild}")

            # Retrieve the ticket_category from config.json
            ticket_category_id = config.get("sell_accounts_category")
            print(f"Ticket category ID from config: {ticket_category_id}")

            if not ticket_category_id:
                await interaction.followup.send("The ticket category is not configured correctly. Please contact an admin.", ephemeral=True)
                print("Ticket category ID not found.")
                return

            # Fetch the category from the guild
            category = discord.utils.get(guild.categories, id=int(ticket_category_id))
            print(f"Category fetched: {category}")

            if not category:
                await interaction.followup.send("The buy accounts category was not found.", ephemeral=True)
                print("Category not found.")
                return

            # Create the private ticket channel using the username
            ticket_channel_name = f"sell-account-{interaction.user.name}"
            print(f"Creating ticket channel: {ticket_channel_name}")
            ticket_channel = await guild.create_text_channel(
                name=ticket_channel_name, category=category)
            print(f"Ticket channel created: {ticket_channel_name}")

            # Set permissions for the ticket channel (private between the user and the bot)
            overwrite = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            await ticket_channel.edit(overwrites=overwrite)
            print("Permissions set.")

            # Pass the offer and payment method to create_skyblock_embed
            api_key = "01f87221-99d0-417a-b62e-b5f855ed7b0b" # Get API Key from config.json
            print(f"Using API key: {api_key}")
            skyblock_embed, stats = await create_skyblock_embed(api_key, ign, None, price=offer, payment_method=payment_method)
            print(f"Skyblock embed created with stats: {stats}")

            # Create an additional info embed with a "Close Ticket" button
            additional_embed = discord.Embed(
                title="Additional Information",
                description="Offer and Payment Details",
                color=discord.Color.blue()
            )
            additional_embed.add_field(name="IGN", value=ign, inline=False)
            additional_embed.add_field(name="Offer", value=f"{offer}", inline=False)
            additional_embed.add_field(name="Payment Method", value=payment_method, inline=False)
            additional_embed.add_field(
                name="Listed By",
                value=f"<@{interaction.user.id}> (ID: {interaction.user.id})",
                inline=False
            )
            additional_embed.set_footer(
                text="Made By airsbw | https://blazecoins.net",
                icon_url="https://images-ext-1.discordapp.net/external/p4mQq0j6A_tLFlpktZMDz8uzhy7ksxUjdTaYw-vVnc0/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/463798421074214914/424f24568e095f05ca84a02c3c75aaae.png"
            )

            # Send the embeds to the private ticket channel
            view = CloseTicketButton()  # View with the close ticket button
            await ticket_channel.send(embed=skyblock_embed)
            await ticket_channel.send(embed=additional_embed, view=view)
            print("Embeds sent to ticket channel.")

            # Save data to the database
            insert_account(
                owner_id=str(interaction.user.id),
                price=offer,
                ign=ign,
                api_key=api_key,
                payment_method=payment_method,
                additional_info=None,
                profile=None,
                channel_id=str(ticket_channel.id),
                channel_name=ticket_channel_name,
                stats=stats  # The fetched Skyblock stats
            )
            print("Account inserted into the database.")

            # Edit the ephemeral message to confirm the ticket creation
            await interaction.followup.send(f"Ticket created successfully! Please check {ticket_channel.mention}.", ephemeral=True)
            print("Confirmation message sent to the user.")

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}. Please try again later.", ephemeral=True)
            print(f"Exception caught: {e}")


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



# Button view for showing the modal
class SellAccountButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Sell an Account", style=discord.ButtonStyle.primary, custom_id="sell_account_button")
    async def open_modal(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            # When the button is clicked, the modal is displayed
            modal = SellAccountModal()
            await interaction.response.send_modal(modal)
        except Exception as e:
            # Notify the user about the error
            await interaction.response.send_message(f"An error occurred while opening the modal: {e}.", ephemeral=True)


# The main cog that handles the ticket system
class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Register persistent views for both the SellAccountButton and CloseTicketButton
        self.bot.add_view(SellAccountButton())
        self.bot.add_view(CloseTicketButton())  # Add persistent view for the Close Ticket button
        print("Persistent views added.")


    # Slash command to start the sell account process (shows an embed with the button)
    @commands.slash_command(name="sellaccount-panel", description="Sends an 'Sell Account' panel.")
    @has_access_role()
    async def sell_account(self, ctx: discord.ApplicationContext):
        try:
            # Create an embed that explains the button
            embed = discord.Embed(
                title="Sell an Account",
                description="Click the button below to provide your details and sell an account.",
                color=discord.Color.green()
            )

            # Send the embed with the button view in the same channel the command was run
            view = SellAccountButton()
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            # Notify the user about the error
            await ctx.send(f"An error occurred: {e}", ephemeral=True)


# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(TicketCog(bot))

