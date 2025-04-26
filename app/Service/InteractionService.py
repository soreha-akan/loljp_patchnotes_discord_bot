from config.constants import ArticleType, ARTICLE_TYPE_NAMES, CommandName

class InteractionService:
    def __init__(self):
        self.article_type_names = {
            ArticleType.LOL_PATCH: "LoLパッチノート",
            ArticleType.TFT_PATCH: "TFTパッチノート",
            ArticleType.LOL_NEWS: "LoLニュース",
            ArticleType.TFT_NEWS: "TFTニュース"
        }

    async def send_followup_in_ephemeral(self, interaction, message):
        await interaction.followup.send(message, ephemeral=True)

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
        if register_result:
            message = self.generate_current_setting_message(register_result, interaction.guild_id, CommandName.START)
        else:
            message = "更新通知が有効になっていません。"
        await interaction.followup.send(message, ephemeral=True)

    async def response_stop(self, interaction, unregister_result):
        if not unregister_result:
            message = "このチャンネルでは更新通知が有効になっていません。"
        else:
            message = self.generate_current_setting_message(unregister_result, interaction.guild_id, CommandName.STOP)
        await interaction.followup.send(message, ephemeral=True)

    async def response_status(self, interaction, current_status):
        message = self.generate_current_setting_message(current_status, interaction.guild_id, CommandName.STATUS)
        await interaction.followup.send(message, ephemeral=True)

    async def response_test(self, interaction, is_complete, count=0):
        if is_complete:
            if count:
                message = "更新通知が有効になっている記事から最新のものを設定されたチャンネルにお送りしました。"
            else:
                message = "更新通知が有効になっていません。"
        else:
            message = "メッセージの送信に失敗しました。 チャンネルの権限で本BOTの発言が許可されているか確認してください。"
        await interaction.followup.send(message, ephemeral=True)

    def generate_current_setting_message(self, current_setting, guild_id, command_name):
        messages = []
        
        messages.append(f"`{command_name}`コマンドが実行されました！")

        base_channel_url = "https://discord.com/channels/" + str(guild_id) + "/"

        for type_key, status_info in current_setting.items():
            article_type_name = ARTICLE_TYPE_NAMES[type_key.value]
            
            if status_info["is_active"]:
                current_channel_url = base_channel_url + str(status_info["channel_id"])
                if status_info["channel_id"] != status_info["channel_id_before"] and status_info["is_active_before"]:
                    old_channel_url = base_channel_url + str(status_info["channel_id_before"])
                    messages.append(f"{article_type_name}の更新通知  -  {old_channel_url} => {current_channel_url}")
                else:
                    messages.append(f"{article_type_name}の更新通知  -  {current_channel_url}")
            else:
                if status_info["is_active_before"]:
                    messages.append(f"{article_type_name}の更新通知  -  **停止しました**")
                else:
                    messages.append(f"{article_type_name}の更新通知  -  **未設定**")
        
        return "\n".join(messages)