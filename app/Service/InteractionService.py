from config.constants import ArticleType, ARTICLE_TYPE_NAMES, CommandName

class InteractionService:
    def __init__(self):
        self.article_type_names = {
            ArticleType.LOL_PATCH: "LoLパッチノート",
            ArticleType.TFT_PATCH: "TFTパッチノート",
            ArticleType.LOL_NEWS: "LoLニュース",
            ArticleType.TFT_NEWS: "TFTニュース"
        }

    async def send_ephemeral_message(self, interaction, message):
        await interaction.response.send_message(message, ephemeral=True)

    async def response_help(self, interaction):
        message = (
            "`/start`\nコマンドを使用したチャンネルで更新通知を有効にします。\n"
            "すでに他のチャンネルで更新通知を利用している場合、発信するチャンネルを変更します。\n\n"
            "`/stop`\nコマンドを使用したチャンネルで更新通知を無効にします。\n\n"
            "`/status`\nbotの稼働状況と更新通知が行われるチャンネルを確認できます。\n\n"
            "`/test`\n更新通知を行っているチャンネルでテストメッセージを送信します。\n\n"
            "`/help`\nコマンドの一覧を表示します。（現在あなたが読んでいるものです。）"
        )
        await interaction.response.send_message(message, ephemeral=True)

    async def response_start(self, interaction, register_result):
        message = self.generate_register_message(register_result, interaction.guild_id, CommandName.START)
        await interaction.response.send_message(message, ephemeral=True)

    async def response_stop(self, interaction, unregister_result):
        message = self.generate_register_message(unregister_result, interaction.guild_id, CommandName.STOP)
        await interaction.response.send_message(message, ephemeral=True)

    async def response_status(self, interaction, current_status):
        message = self.generate_register_message(current_status, interaction.guild_id, CommandName.STATUS)
        await interaction.response.send_message(message, ephemeral=True)

    def generate_register_message(self, register_result, guild_id, command_name):
        """登録結果に基づいてメッセージを生成"""
        messages = []
        
        messages.append(f"`{command_name}`コマンドが実行されました！")

        base_channel_url = "https://discord.com/channels/" + str(guild_id) + "/"

        for article_type in register_result:
            article_type_name = ARTICLE_TYPE_NAMES[article_type.article_type]
            if article_type.is_active:
                current_channel_url = base_channel_url + str(article_type.channel.id)
                if article_type.is_channel_change:
                    old_channel_url = base_channel_url + str(article_type.old_channel_id)
                    messages.append(f"{article_type_name} の更新通知 {old_channel_url} => {current_channel_url}")
                else:
                    messages.append(f"{article_type_name} の更新通知 {current_channel_url}")
            else:
                if article_type.is_stopped:
                    messages.append(f"{article_type_name} の更新通知を停止")
                else:
                    messages.append(f"{article_type_name} の更新通知 **未設定**")
        
        return "\n".join(messages)
