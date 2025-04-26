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
        self.send_message_service = SendMessageService(bot)

    # ToDo コマンド実行時に権限チェック（チャンネルでの発言権とか）いれる？

    @app_commands.command(name="help", description="コマンドの一覧を表示します。")
    @app_commands.default_permissions(administrator=True)
    async def help_command(self, interaction: discord.Interaction):
        await self.interaction_service.response_help(interaction)

    @app_commands.command(name="start", description="更新のお知らせ設定を開始します。")
    @app_commands.default_permissions(administrator=True)
    async def start_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        current = self.manage_guild_service.fetch_status_by_channel(interaction)
        initial = [
            at for at, info in current.items()
            if info["is_active"]
        ]

        view = NotificationPanelView(
            self.manage_guild_service,
            self.interaction_service,
            initial_selected=initial
        )
        await interaction.followup.send(
            "通知を開始するタイプを選択してください (複数選択可):",
            view=view,
            ephemeral=True
        )

    @app_commands.command(
        name="stop",
        description="このチャンネルで行われている更新のお知らせを停止します。",
    )
    @app_commands.default_permissions(administrator=True)
    async def stop_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        unregister_result = self.manage_guild_service.unregister_channel(interaction)

        await self.interaction_service.response_stop(interaction, unregister_result)

    @app_commands.command(name="status", description="botの稼働状況を表示します。")
    @app_commands.default_permissions(administrator=True)
    async def status_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        current_status = self.manage_guild_service.fetch_current_status(interaction)

        await self.interaction_service.response_status(interaction, current_status)

    @app_commands.command(name="test", description="テストメッセージを送信します。")
    @app_commands.default_permissions(administrator=True)
    async def test_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            count = await self.check_update_service.send_test_message(interaction.guild_id)
            await self.interaction_service.response_test(interaction, True, count)
        except:
            await self.interaction_service.response_test(interaction, False)

        '''
        ToDo エラーハンドリングとか
            except Exception as e:
                print(f"テストコマンド実行中にエラーが発生しました: {e}")
            みたいな感じでエラーを取得できる

            エラーの内容をパターン化して、ユーザーに解決方法を伝えるようにしたいね
        '''


class NotificationPanelView(discord.ui.View):
    def __init__(
        self,
        manage_guild_service: ManageGuildService,
        interaction_service: InteractionService,
        initial_selected: list[ArticleType] | None = None,
        timeout: float = 120,
    ):
        super().__init__(timeout=timeout)
        self.manage_guild_service = manage_guild_service
        self.interaction_service = interaction_service

        # 初期選択セット
        self.selected: set[ArticleType] = set(initial_selected or [])

        # ボタンのラベル定義
        labels = {
            ArticleType.LOL_PATCH: "LoL パッチノート",
            ArticleType.TFT_PATCH: "TFT パッチノート",
            ArticleType.LOL_NEWS:  "LoL ニュース",
            ArticleType.TFT_NEWS:  "TFT ニュース",
        }

        # タイプ別ボタンを生成
        for article_type, label in labels.items():
            # 初期スタイルは selected 判定
            style = (
                discord.ButtonStyle.primary
                if article_type in self.selected
                else discord.ButtonStyle.secondary
            )
            button = discord.ui.Button(
                label=label,
                style=style,
                custom_id=article_type.name
            )
            button.callback = self._make_toggle_callback(article_type, button)
            self.add_item(button)

        # 「選択完了」ボタンの enabled/disabled は selected の有無で
        self.confirm_button = discord.ui.Button(
            label="選択完了",
            style=discord.ButtonStyle.success,
            disabled=len(self.selected) == 0,
            custom_id="confirm_selection"
        )
        self.confirm_button.callback = self._on_confirm
        self.add_item(self.confirm_button)

    def _make_toggle_callback(self, article_type: ArticleType, button: discord.ui.Button):
        async def toggle(interaction: discord.Interaction):
            if article_type in self.selected:
                self.selected.remove(article_type)
                button.style = discord.ButtonStyle.secondary
            else:
                self.selected.add(article_type)
                button.style = discord.ButtonStyle.primary

            # 確定ボタンの有効/無効更新
            self.confirm_button.disabled = len(self.selected) == 0
            await interaction.response.edit_message(view=self)
        return toggle

    async def _on_confirm(self, interaction: discord.Interaction):
        article_types = list(self.selected)
        register_result = self.manage_guild_service.register_channel(interaction, article_types)
        await interaction.response.edit_message(content="設定を更新します！",view=None)
        await self.interaction_service.response_start(interaction, register_result)
        self.stop()