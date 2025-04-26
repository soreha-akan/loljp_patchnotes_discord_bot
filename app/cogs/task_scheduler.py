from discord.ext import commands, tasks
from Service.CheckUpdateService import CheckUpdateService


class TaskScheduler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_update_service = CheckUpdateService(bot)
        self.check_updates_loop.start()

    async def cog_unload(self):
        self.check_updates_loop.cancel()
        
    @tasks.loop(minutes=15)
    async def check_updates_loop(self):
        await self.check_update_service.check_updates()
