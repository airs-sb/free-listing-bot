import os
import shutil
import subprocess
import json
import discord
from discord.commands import slash_command
from discord.ext import commands
from utils.database import init_db
from utils.venv import get_venv_python
from discord.errors import HTTPException, LoginFailure

conn, c = init_db()

class BotSetup(commands.Cog):
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

    @slash_command(name="create", description="Set up a new bot with configurations")
    async def setup_bot(self, ctx, 
                        access_role: discord.Role,
                        non_role: discord.Role,
                        sell_accounts_category: discord.CategoryChannel,
                        buy_accounts_category: discord.CategoryChannel,
                        middleman_category: discord.CategoryChannel,
                        profile_sell_category: discord.CategoryChannel,
                        profile_buy_category: discord.CategoryChannel,
                        mfa_category: discord.CategoryChannel,
                        coin_category: discord.CategoryChannel,
                        accounts_category: discord.CategoryChannel,
                        profiles_category: discord.CategoryChannel,
                        bedwars_category: discord.CategoryChannel,
                        ticket_logs_channel: discord.TextChannel,
                        coin_price_buy: str,
                        coin_price_sell: str,
                        allow_membership: bool,
                        membership_price: str,
                        membership_fee: str,
                        bot_token: str,
                        bot_name: str,
                        venv_name: str):

        # Check if the user has enough credits
        user_credits = self.load_credits(ctx.author.id)
        if user_credits <= 0:
            embed = discord.Embed(title="Insufficient Credits", description="You don't have enough credits to create a bot.", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # Proceed with the bot setup (we won't deduct the credit yet, only if the process succeeds)
        try:
            # Create the folder for the new bot
            new_bot_folder = os.path.join("bots", bot_name)
            os.makedirs(new_bot_folder, exist_ok=True)

            # Copy all files and directories from "files" folder to the new bot folder
            files_folder = "files"
            if os.path.exists(files_folder):
                for item_name in os.listdir(files_folder):
                    source_item = os.path.join(files_folder, item_name)
                    destination_item = os.path.join(new_bot_folder, item_name)
                    
                    if os.path.isfile(source_item):
                        shutil.copy2(source_item, destination_item)
                    elif os.path.isdir(source_item):
                        if os.path.exists(destination_item):
                            shutil.rmtree(destination_item)
                        shutil.copytree(source_item, destination_item)
            else:
                await ctx.respond(f"Error: Could not find the 'files' folder", ephemeral=True)
                return

            # Create config.json with the provided parameters
            config_path = os.path.join(new_bot_folder, "config.json")
            config_data = {
                "access_role": access_role.id,
                "non_role": non_role.id,
                "sell_accounts_category": sell_accounts_category.id,
                "buy_accounts_category": buy_accounts_category.id,
                "middleman_category": middleman_category.id,
                "profile_sell_category": profile_sell_category.id,
                "profile_buy_category": profile_buy_category.id,
                "mfa_category": mfa_category.id,
                "coin_category": coin_category.id,
                "accounts_category": accounts_category.id,
                "profiles_category": profiles_category.id,
                "bedwars_category": bedwars_category.id,
                "ticket_logs_channel": ticket_logs_channel.id,
                "coin_price_buy": coin_price_buy,
                "coin_price_sell": coin_price_sell,
                "allow_membership": allow_membership,
                "membership_price": membership_price,
                "membership_fee": membership_fee,
                "token": bot_token,
                "prefix": "!",
                "owner_id": ctx.author.id
            }

            with open(config_path, "w") as config_file:
                json.dump(config_data, config_file)

            # Ensure the config.json and bot.py exist before starting the bot
            bot_file_name = "bot.py"
            
            if os.path.exists(os.path.join(new_bot_folder, bot_file_name)) and os.path.exists(config_path):
                # Get the Python executable from the virtual environment
                try:
                    venv_python = get_venv_python(venv_name)
                except FileNotFoundError as e:
                    await ctx.respond(f"Error: {str(e)}", ephemeral=True)
                    return
                
                # Start the bot using subprocess in the correct directory and venv's python
                try:
                    # Validate the bot token first
                    test_bot = discord.Client(intents=discord.Intents.default())
                    await test_bot.login(bot_token)  # Will throw error if token is invalid
                    await test_bot.close()

                    # If token is valid, proceed to run the bot in subprocess
                    subprocess.Popen([venv_python, bot_file_name], cwd=new_bot_folder)

                    # Now we deduct the credit since everything went well
                    self.update_credits(ctx.author.id, user_credits - 1)

                    embed = discord.Embed(
                        title="Bot Creation Success",
                        description=f"Bot `{bot_name}` has been created and started! You have {user_credits - 1} credits left.",
                        color=discord.Color.green()
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                except LoginFailure:
                    embed = discord.Embed(
                        title="Invalid Token",
                        description="The bot token you provided is invalid. Please provide a valid token.",
                        color=discord.Color.red()
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                    shutil.rmtree(new_bot_folder)  # Clean up if bot creation fails
                except Exception as e:
                    embed = discord.Embed(
                        title="Error",
                        description=f"An error occurred: {str(e)}",
                        color=discord.Color.red()
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                    shutil.rmtree(new_bot_folder)  # Clean up if bot creation fails
            else:
                await ctx.respond(f"Error: Could not find {bot_file_name} or {config_path}", ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="Setup Failed",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(BotSetup(bot))
