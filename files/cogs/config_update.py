import discord
from discord.ext import commands
import json
from typing import Union
import utils.reloadConfig as config_manager
from cogs.address import has_access_role

# Helper function to load and save the config file
def load_config():
    with open("config.json", "r") as config_file:
        return json.load(config_file)

def save_config(data):
    with open("config.json", "w") as file:
        json.dump(data, file, indent=4)

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash Command Group for /config
    config = discord.SlashCommandGroup("config", "Configuration commands")

    # Choices for each command - customize these for your config.json
    CATEGORY_CHOICES = [
        discord.OptionChoice(name="Coins Category", value="coin_category"),
        discord.OptionChoice(name="Accounts Category", value="accounts_category"),
        discord.OptionChoice(name="Profiles Category", value="profiles_category"),
        discord.OptionChoice(name="Bedwars Category", value="bedwars_category"),
        discord.OptionChoice(name="MFA Category", value="mfa_category"),
        discord.OptionChoice(name="Profile Buy Category", value="profile_buy_category"),
        discord.OptionChoice(name="Profile Sell Category", value="profile_sell_category"),
        discord.OptionChoice(name="Middleman Category", value="middleman_category"),
        discord.OptionChoice(name="Buy Account Category", value="buy_accounts_category"),
        discord.OptionChoice(name="Sell Account Category", value="sell_accounts_category"),
    ]
    
    ROLE_CHOICES = [
        discord.OptionChoice(name="Seller Role", value="access_role"),
        discord.OptionChoice(name="Customer Role", value="non_role"),
    ]
    
    CHANNEL_CHOICES = [
        discord.OptionChoice(name="Ticket Logs", value="ticket_logs_channel"),
        discord.OptionChoice(name="Vouch Channel", value="vouch_channel"),
    ]
    
    VALUE_CHOICES = [
        discord.OptionChoice(name="Membership Price", value="membership_price"),
        discord.OptionChoice(name="Membership Fee", value="membership_fee"),
        discord.OptionChoice(name="Coin Buy Price", value="coin_buy_price"),
        discord.OptionChoice(name="Coin Sell Price", value="coin_sell_price"),
    ]

    @config.command(name="update-category", description="Update a category in the config")
    @has_access_role()
    async def update_category(
        self,
        ctx: discord.ApplicationContext,
        key: discord.Option(str, "The key to update", choices=CATEGORY_CHOICES),
        category: discord.Option(discord.CategoryChannel, "The category to set"),
    ):
        await self.update_config(ctx, key, category.id)

    @config.command(name="update-role", description="Update a role in the config")
    @has_access_role()
    async def update_role(
        self,
        ctx: discord.ApplicationContext,
        key: discord.Option(str, "The key to update", choices=ROLE_CHOICES),
        role: discord.Option(discord.Role, "The role to set"),
    ):
        await self.update_config(ctx, key, role.id)

    @config.command(name="update-channel", description="Update a channel in the config")
    @has_access_role()
    async def update_channel(
        self,
        ctx: discord.ApplicationContext,
        key: discord.Option(str, "The key to update", choices=CHANNEL_CHOICES),
        channel: discord.Option(discord.TextChannel, "The channel to set"),
    ):
        await self.update_config(ctx, key, channel.id)

    @config.command(name="update-value", description="Update a string value in the config")
    @has_access_role()
    async def update_value(
        self,
        ctx: discord.ApplicationContext,
        key: discord.Option(str, "The key to update", choices=VALUE_CHOICES),
        value: discord.Option(str, "The value to set"),
    ):
        await self.update_config(ctx, key, value)

    # Helper method to update the config file and send feedback
    async def update_config(self, ctx: discord.ApplicationContext, key: str, value: Union[int, str]):
        config = load_config()
        
        # Update or create the key with the new value
        config[key] = value
        save_config(config)
        
        # Reload config to apply the changes
        config_manager.reload_config()
        
        # Respond with the updated value confirmation
        await ctx.respond(f"Updated Config! Please use /restart for it to process.")

def setup(bot):
    bot.add_cog(ConfigCog(bot))
