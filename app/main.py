import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import discord
from dotenv import load_dotenv
from discord.ext import commands
from keep_alive import keep_alive

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.typing = False
        intents.presences = False
        intents.message_content = True
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

    async def setup_hook(self):
        from cogs.event import Event
        from cogs.command import Command
        from cogs.task_scheduler import TaskScheduler

        await self.add_cog(Event(self))
        await self.add_cog(Command(self))
        await self.add_cog(TaskScheduler(self))

        await self.tree.sync()

keep_alive()
load_dotenv()
TOKEN = os.environ["DISCORD_BOT_TOKEN"]
bot = DiscordBot()

bot.run(TOKEN)
