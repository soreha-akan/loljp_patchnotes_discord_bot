import discord
from discord.ext import commands
from discord import app_commands
from config.constants import ArticleType
from Service.InteractionService import InteractionService
from Service.ManageGuildService import ManageGuildService
from Service.CheckUpdateService import CheckUpdateService
from Service.SendMessageService import SendMessageService

class Command(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.interaction_service = InteractionService()
        self.manage_guild_service = ManageGuildService()
        self.check_update_service = CheckUpdateService(bot)
        self.send_messsage_service = SendMessageService(bot)

    # ToDo コマンド実行時に権限チェック（チャンネルでの発言権とか）いれる？

    @app_commands.command(name="help", description="コマンドの一覧を表示します。")
    @app_commands.default_permissions(administrator=True)
    async def help_command(self, interaction: discord.Interaction):
        await self.interaction_service.response_help(interaction)

    @app_commands.command(name="start", description="更新のお知らせを開始します。")
    @app_commands.describe(
        lol_patch="LoLパッチノートを有効にする",
        tft_patch="TFTパッチノートを有効にする",
        lol_news="LoLニュースを有効にする",
        tft_news="TFTニュースを有効にする"
    )
    @app_commands.default_permissions(administrator=True)
    async def start_command(
        self,
        interaction: discord.Interaction,
        lol_patch: bool = False,
        tft_patch: bool = False,
        lol_news: bool = False,
        tft_news: bool = False
    ):
        selected_article_type = []
        if lol_patch: selected_article_type.append(ArticleType.LOL_PATCH)
        if tft_patch: selected_article_type.append(ArticleType.TFT_PATCH)
        if lol_news: selected_article_type.append(ArticleType.LOL_NEWS)
        if tft_news: selected_article_type.append(ArticleType.TFT_NEWS)
        
        if not selected_article_type:
            message = "通知タイプを１件以上選択してください。"
            await self.interaction_service.send_ephemeral_message(interaction, message)
            return

        
        register_result = self.manage_guild_service.register_channel(interaction, selected_article_type)
        
        await self.interaction_service.response_start(interaction, register_result)

    @app_commands.command(name="stop", description="このチャンネルで行われている更新のお知らせを停止します。")
    @app_commands.default_permissions(administrator=True)
    async def stop_command(self, interaction: discord.Interaction):
        unregister_result = self.manage_guild_service.unregister_channel(interaction)
        
        await self.interaction_service.response_stop(interaction, unregister_result)
        
    @app_commands.command(name="status", description="botの稼働状況を表示します。")
    @app_commands.default_permissions(administrator=True)
    async def status_command(self, interaction: discord.Interaction):
        current_status = self.manage_guild_service.fetch_current_status(interaction)
        
        await self.interaction_service.response_status(interaction, current_status)
        
        
    @app_commands.command(name="test", description="テストメッセージを送信します。")
    @app_commands.default_permissions(administrator=True)
    async def test_command(self, interaction: discord.Interaction):
        try:
            await self.check_update_service.send_test_message(interaction.guild_id)
        except:
            message = "メッセージの送信に失敗しました。 チャンネルの権限で本BOTの発言が許可されているか確認してください。"
            await self.interaction_service.send_ephemeral_message(interaction, message)
        
    