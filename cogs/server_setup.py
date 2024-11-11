import discord
from discord.commands import slash_command
from discord.ext import commands

class ServerSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Ensure the user has admin permissions
    async def has_admin_permissions(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("You don't have the required permissions to run this command.", ephemeral=True)
            return False
        return True

    @slash_command(name="setup-server", description="Set up categories and channels for the bot")
    async def setup_server(self, ctx):
        # Check if user has admin permissions
        if not await self.has_admin_permissions(ctx):
            return

        # Initial embed
        embed = discord.Embed(
            title="Server Setup",
            description="Setting up categories and channels...",
            color=discord.Color.blue()
        )
        embed.add_field(name="Progress", value="Starting setup...", inline=False)
        message = await ctx.respond(embed=embed)

        # Categories to create
        category_names = [
            "Sell Accounts",
            "Buy Accounts",
            "Middleman",
            "Profile Sell",
            "Profile Buy",
            "MFA",
            "Coins",
            "Accounts",
            "Profiles",
            "Bedwars",
            "Ticket Logs"
        ]

        created_categories = {}

        # Create the categories and update embed progress
        for index, category_name in enumerate(category_names, start=1):
            category = await ctx.guild.create_category(name=category_name)
            created_categories[category_name] = category

            # Update the embed with progress
            embed.set_field_at(
                0, 
                name="Progress", 
                value=f"Created category: **{category_name}** ({index}/{len(category_names)})", 
                inline=False
            )
            await message.edit_original_message(embed=embed)

        # Create a ticket logs channel inside the "Ticket Logs" category
        ticket_logs_channel = await created_categories["Ticket Logs"].create_text_channel(name="ticket-logs")
        embed.set_field_at(
            0, 
            name="Progress", 
            value=f"Created channel: **ticket-logs** inside Ticket Logs category", 
            inline=False
        )
        await message.edit_original_message(embed=embed)

        # Finalize the embed
        embed.title = "Server Setup Complete"
        embed.color = discord.Color.green()
        embed.set_field_at(
            0, 
            name="Progress", 
            value="All categories and channels have been successfully created!",
            inline=False
        )
        await message.edit_original_message(embed=embed)

def setup(bot):
    bot.add_cog(ServerSetup(bot))
