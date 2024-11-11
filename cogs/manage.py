import discord
from discord.ext import commands
import os
import subprocess
import psutil  # Ensure psutil is installed
import sys
import platform

class BotManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Determine the path to the Python executable in the current environment (venv)
        if platform.system() == 'Windows':
            python_executable = os.path.join(sys.prefix, 'Scripts', 'python.exe')
        else:
            python_executable = os.path.join(sys.prefix, 'bin', 'python')

        # Normalize the path for comparison
        self.python_executable = os.path.normpath(python_executable)

    async def bot_name_autocomplete(self, ctx: discord.AutocompleteContext):
        # Autocomplete function to list available bot folders containing bot.py in 'bots' directory
        current_dir = os.getcwd()
        bots_dir = os.path.join(current_dir, "bots")
        bot_names = []
        if os.path.isdir(bots_dir):
            for name in os.listdir(bots_dir):
                bot_path = os.path.join(bots_dir, name)
                bot_file = os.path.join(bot_path, "bot.py")
                if os.path.isdir(bot_path) and os.path.isfile(bot_file):
                    bot_names.append(name)
        return [bot_name for bot_name in bot_names if bot_name.startswith(ctx.value.lower())]

    def is_bot_running(self, bot_name):
        bots_dir = os.path.join(os.getcwd(), "bots")
        bot_path = os.path.abspath(os.path.join(bots_dir, bot_name))

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd', 'exe']):
            try:
                cmdline = proc.info['cmdline']
                cwd = proc.info['cwd']
                exe = proc.info['exe']
                if cmdline and cwd and exe:
                    # Normalize paths
                    proc_cwd = os.path.abspath(cwd)
                    proc_exe = os.path.normpath(exe)

                    if (proc_cwd == bot_path and
                        proc_exe == self.python_executable and
                        any('bot.py' in arg for arg in cmdline)):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False

    def get_bot_processes(self, bot_name):
        # Returns a list of processes corresponding to the bot
        bot_processes = []
        bots_dir = os.path.join(os.getcwd(), "bots")
        bot_path = os.path.abspath(os.path.join(bots_dir, bot_name))

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd', 'exe']):
            try:
                cmdline = proc.info['cmdline']
                cwd = proc.info['cwd']
                exe = proc.info['exe']
                if cmdline and cwd and exe:
                    # Normalize paths
                    proc_cwd = os.path.abspath(cwd)
                    proc_exe = os.path.normpath(exe)

                    if (proc_cwd == bot_path and
                        proc_exe == self.python_executable and
                        any('bot.py' in arg for arg in cmdline)):
                        bot_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return bot_processes

    @commands.slash_command(name="manage_bot", description="Start, stop, or restart a bot.")
    @discord.option(
        "action",
        description="Action to perform",
        choices=["start", "stop", "restart"]
    )
    @discord.option(
        "bot_name",
        description="Name of the bot",
        autocomplete=bot_name_autocomplete
    )
    async def manage_bot(self, ctx, action: str, bot_name: str):
        await ctx.defer()  # Defer the response if the operation takes time

        # Determine the path to the bot's directory and bot.py file
        current_dir = os.getcwd()
        bots_dir = os.path.join(current_dir, "bots")
        bot_path = os.path.abspath(os.path.join(bots_dir, bot_name))
        bot_file = os.path.join(bot_path, "bot.py")

        # Validate that the bot directory and bot.py file exist
        if not os.path.isdir(bot_path):
            await ctx.send_followup(f"❌ Bot `{bot_name}` does not exist in the 'bots' directory.")
            return
        if not os.path.isfile(bot_file):
            await ctx.send_followup(f"❌ No `bot.py` found in `{bot_name}` folder.")
            return

        # Handle the requested action
        if action == "start":
            if self.is_bot_running(bot_name):
                await ctx.send_followup(f"⚠️ Bot `{bot_name}` is already running.")
            else:
                # Start the bot process using the same Python executable
                subprocess.Popen([self.python_executable, "bot.py"], cwd=bot_path)
                await ctx.send_followup(f"✅ Bot `{bot_name}` started successfully.")
        elif action == "stop":
            bot_processes = self.get_bot_processes(bot_name)
            if bot_processes:
                for proc in bot_processes:
                    try:
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)  # Ensure the process has terminated
                        except psutil.TimeoutExpired:
                            proc.kill()  # Force kill if it doesn't terminate
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                await ctx.send_followup(f"🛑 Bot `{bot_name}` has been stopped.")
            else:
                await ctx.send_followup(f"⚠️ Bot `{bot_name}` is not running.")
        elif action == "restart":
            bot_processes = self.get_bot_processes(bot_name)
            if bot_processes:
                for proc in bot_processes:
                    try:
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                stop_message = f"🔄 Bot `{bot_name}` was running and has been stopped."
            else:
                stop_message = f"🔄 Bot `{bot_name}` was not running."
            # Start the bot process using the same Python executable
            subprocess.Popen([self.python_executable, "bot.py"], cwd=bot_path)
            await ctx.send_followup(f"{stop_message}\n✅ Bot `{bot_name}` restarted successfully.")

def setup(bot):
    bot.add_cog(BotManager(bot))
