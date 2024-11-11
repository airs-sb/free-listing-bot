import discord
from discord.ext import commands
import random
import json
from cogs.address import has_access_role

# Load config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Modal to collect details for the middleman request
class RequestMiddlemanModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Request a Middleman")

        # Modal fields
        self.add_item(discord.ui.InputText(label="Other User ID", placeholder="Enter the ID of the other party", required=True))
        self.add_item(discord.ui.InputText(label="Deal Amount", placeholder="Enter the deal amount", required=True))

    async def callback(self, interaction: discord.Interaction):
        try:
            # Ephemeral message informing that the ticket is being created
            await interaction.response.send_message("Creating ticket... Please wait.", ephemeral=True)

            # Retrieve input from modal
            other_user_id = self.children[0].value
            deal_amount = self.children[1].value
            guild = interaction.guild

            # Retrieve the ticket category from config.json
            ticket_category_id = config.get("middleman_category")

            if not ticket_category_id:
                await interaction.followup.send("The ticket category is not configured correctly. Please contact an admin.", ephemeral=True)
                return

            # Fetch the category from the guild
            category = discord.utils.get(guild.categories, id=int(ticket_category_id))

            if not category:
                await interaction.followup.send("The ticket category was not found.", ephemeral=True)
                return

            # Create the private ticket channel using the username
            ticket_channel_name = f"middleman-{interaction.user.name}"
            ticket_channel = await guild.create_text_channel(name=ticket_channel_name, category=category)

            # Fetch the other user by ID
            other_user = await guild.fetch_member(int(other_user_id))

            # Set permissions for the ticket channel (private between the user, other user, and the bot)
            overwrite = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                other_user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            await ticket_channel.edit(overwrites=overwrite)

            # Create an embed for the ticket with the deal amount
            ticket_embed = discord.Embed(
                title="Middleman Request",
                description="A new middleman request has been created.",
                color=discord.Color.dark_gray()
            )
            ticket_embed.add_field(name="Deal Amount", value=f"${deal_amount}", inline=False)
            ticket_embed.set_footer(text="Click the button below to close the ticket.")

            # Send the embed with the close ticket button in the channel
            view = CloseTicketButton()
            await ticket_channel.send(embed=ticket_embed, view=view)

            # Confirm the ticket has been created
            await interaction.followup.send(f"Ticket created successfully! Check {ticket_channel.mention}.", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}. Please try again later.", ephemeral=True)


# Button view for closing the ticket
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


# Button view for initiating the middleman request
class RequestMiddlemanButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Request Middleman", style=discord.ButtonStyle.danger, custom_id="request_middleman_button")
    async def request_middleman(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            # When the button is clicked, the modal is displayed
            modal = RequestMiddlemanModal()
            await interaction.response.send_modal(modal)
        except Exception as e:
            # Notify the user about the error
            await interaction.response.send_message(f"An error occurred while opening the modal: {e}.", ephemeral=True)


# Main cog that handles the ticket system
class MiddlemanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Add persistent view when the bot is ready
        self.bot.add_view(RequestMiddlemanButton())
        self.bot.add_view(CloseTicketButton())  # Persistent view for closing the ticket
        print("Persistent views added.")

    # Command to start the middleman process (shows an embed with the button)
    @commands.slash_command(name="middleman-panel", description="Sends a middleman panel.")
    @has_access_role()
    async def middleman(self, ctx: discord.ApplicationContext):
        try:
            # Create an embed with the request middleman button
            embed = discord.Embed(
                title="Request a Middleman",
                description="To request a middleman, press the button below.",
                color=discord.Color.dark_gray()
            )

            # Send the embed with the button view in the same channel the command was run
            view = RequestMiddlemanButton()
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            # Notify the user about the error
            await ctx.send(f"An error occurred: {e}", ephemeral=True)


# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(MiddlemanCog(bot))

