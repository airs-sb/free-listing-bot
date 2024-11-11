import discord
from discord.ext import commands
from cogs.address import has_access_role

# Modal to collect amount and payment method
class PaymentModal(discord.ui.Modal):
    def __init__(self, rank, price):
        self.rank = rank
        self.price = price
        super().__init__(title=f"Payment Details for {rank}")

        self.add_item(discord.ui.InputText(label="Amount", placeholder="Enter the amount", required=True))
        self.add_item(discord.ui.InputText(label="Payment Method", placeholder="Enter your payment method", required=True))

    async def callback(self, interaction: discord.Interaction):
        try:
            # Retrieve input
            amount = int(self.children[0].value)
            payment_method = self.children[1].value

            # Calculate total price
            total_price = amount * self.price

            # Create a ticket channel
            guild = interaction.guild
            ticket_channel_name = f"mfa-ticket-{interaction.user.name}"
            ticket_channel = await guild.create_text_channel(name=ticket_channel_name)

            # Set permissions for the ticket channel (private between the user and the bot)
            overwrite = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            await ticket_channel.edit(overwrites=overwrite)

            # Create the ticket embed
            ticket_embed = discord.Embed(
                title="MFA Ticket",
                description=f"Ticket for {self.rank}",
                color=discord.Color.blue()
            )
            ticket_embed.add_field(name="Amount", value=str(amount), inline=False)
            ticket_embed.add_field(name="Total Price", value=f"${total_price:.2f}", inline=False)
            ticket_embed.add_field(name="Payment Method", value=payment_method, inline=False)
            ticket_embed.set_footer(text="Click the button below to close the ticket.")

            # Send the embed with a close ticket button
            view = CloseTicketButton()
            await ticket_channel.send(embed=ticket_embed, view=view)

            # Confirm ticket creation to the user
            await interaction.response.send_message(f"Ticket created successfully! Check {ticket_channel.mention}.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}.", ephemeral=True)


# Dropdown menu for selecting the rank
class RankDropdown(discord.ui.Select):
    def __init__(self, rank_prices):
        # Dropdown options with prices in descriptions
        options = [
            discord.SelectOption(label="Unranked", description=f"${rank_prices['Unranked']}"),
            discord.SelectOption(label="VIP", description=f"${rank_prices['VIP']}"),
            discord.SelectOption(label="VIP+", description=f"${rank_prices['VIP+']}"),
            discord.SelectOption(label="MVP", description=f"${rank_prices['MVP']}"),
            discord.SelectOption(label="MVP+", description=f"${rank_prices['MVP+']}"),
            discord.SelectOption(label="MVP++", description=f"${rank_prices['MVP++']}")
        ]
        super().__init__(placeholder="Select a rank...", options=options, custom_id="rank_dropdown")  # Apply custom_id to the dropdown
        self.rank_prices = rank_prices

    async def callback(self, interaction: discord.Interaction):
        # Get the selected rank
        selected_rank = self.values[0]
        price = self.rank_prices[selected_rank]

        # Show the modal to collect payment details
        modal = PaymentModal(rank=selected_rank, price=price)
        await interaction.response.send_modal(modal)


# View containing the dropdown
class RankDropdownView(discord.ui.View):
    def __init__(self, rank_prices):
        super().__init__(timeout=None)
        self.add_item(RankDropdown(rank_prices))  # Add dropdown to the view


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


# Main cog that handles the MFA panel
class MFACog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Add persistent view when the bot is ready
        self.bot.add_view(RankDropdownView({
            "Unranked": 4.5, "VIP": 9.99, "VIP+": 19.99, "MVP": 29.99, "MVP+": 39.99, "MVP++": 49.99
        }))  # Example default prices for restoration after restart
        self.bot.add_view(CloseTicketButton())  # Add persistent close ticket view
        print("Persistent views added.")

    # Command to start the MFA process (shows an embed with the dropdown)
    @commands.slash_command(name="mfa-panel", description="Sends an MFA panel.")
    @has_access_role()
    async def mfa(self, ctx: discord.ApplicationContext,
                  non_price: float, vip_price: float, vip_plus_price: float,
                  mvp_price: float, mvp_plus_price: float, mvp_plus_plus_price: float):
        try:
            # Set the rank prices based on the options provided in the command
            rank_prices = {
                "Unranked": non_price,
                "VIP": vip_price,
                "VIP+": vip_plus_price,
                "MVP": mvp_price,
                "MVP+": mvp_plus_price,
                "MVP++": mvp_plus_plus_price
            }

            # Create an embed with the rank options and prices displayed
            embed = discord.Embed(
                title="Request a Rank",
                description=(
                    f"[**Unranked**] | {rank_prices['Unranked']}$\n"
                    f"[**VIP**] | {rank_prices['VIP']}$\n"
                    f"[**VIP+**] | {rank_prices['VIP+']}$\n"
                    f"[**MVP**] | {rank_prices['MVP']}$\n"
                    f"[**MVP+**] | {rank_prices['MVP+']}$\n"
                    f"[**MVP++**] | {rank_prices['MVP++']}$"
                ),
                color=discord.Color.dark_gray()
            )

            # Send the embed with the dropdown view separately (not as a reply)
            view = RankDropdownView(rank_prices)
            await ctx.send(embed=embed, view=view)  # Send separately, not replying to the command

        except Exception as e:
            # Notify the user about the error
            await ctx.send(f"An error occurred: {e}")  # Use ctx.send without ephemeral here


# Setup function to add the cog to the bot
def setup(bot):
    bot.add_cog(MFACog(bot))

