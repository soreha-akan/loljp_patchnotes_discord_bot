from discord.ext import commands
from Service.ManageGuildService import ManageGuildService
from Service.CheckUpdateService import CheckUpdateService


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manage_guild_service = ManageGuildService()
        self.check_update_service = CheckUpdateService(bot)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.manage_guild_service.handle_guild_join(guild.id, guild.name)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.manage_guild_service.handle_guild_remove(guild.id)
