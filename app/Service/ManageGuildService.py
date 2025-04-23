from app.Models.Guild import Guild
from DAO.GuildDAO import GuildDAO
from DAO.GuildChannelDAO import GuildChannelDAO
from config.constants import ArticleType

class ManageGuildService:
    def __init__(self):
        self.guild_dao = GuildDAO()
        self.guild_channel_dao = GuildChannelDAO()

    def handle_guild_join(self, guild_id: int, name: str):
        existing = self.guild_dao.get_by_guild_id(guild_id)

        if existing:
            self.guild_dao.update_by_conditions(
                conditions={
                    Guild.guild_id: guild_id,
                },
                values={
                    Guild.name: name,
                    Guild.deleted: False,
                    Guild.deleted_at: None,
                }
            )
        else:
            self.guild_dao.insert_guild(guild_id, name)

    def handle_guild_remove(self, guild_id: int):
        result = self.guild_dao.soft_delete_by_guild_id(guild_id)
        # Guildに紐付くGuildChannelを論理削除
        if result:
            self.guild_channel_dao.soft_delete_by_guild_id(guild_id)

    def register_channel(self, interaction, selected_article_types):
        channels = self.guild_channel_dao.get_by_guild_id(interaction.guild_id)
        result = {}
        all_article_types = [
            ArticleType.LOL_PATCH,
            ArticleType.TFT_PATCH,
            ArticleType.LOL_NEWS,
            ArticleType.TFT_NEWS
        ]
        
        for article_type in all_article_types:
            # コマンドで選択されたタイプかどうか確認
            is_selected = article_type in selected_article_types
            
            # 既存のチャンネル設定を取得
            existing_channel = None
            for channel in channels:
                if article_type == channel.article_type:
                    existing_channel = channel
                    break
            
            # 処理パターンに応じた分岐
            if existing_channel:
                # 既存の設定がある場合
                if is_selected:
                    # コマンドで選択された場合
                    if existing_channel.is_active is True and existing_channel.discord_channel_id == interaction.channel_id:
                        # パターン1: 既存設定があり、アクティブで、同じチャンネル
                        self.guild_channel_dao.update_channel_by_id(
                            existing_channel.id,
                            {
                                "is_active": True,
                                "channel_id": interaction.channel_id,
                                "name": interaction.channel.name,
                            }
                        )
                        result[article_type] = {
                            "article_type": article_type,
                            "is_active": True,
                            "is_channel_change": False,
                            "channel_id": interaction.channel_id
                        }
                    elif existing_channel.is_active is not True:
                        # パターン2: 既存設定があり、非アクティブ
                        self.guild_channel_dao.update_channel_by_id(
                            existing_channel.id,
                            {
                                "is_active": True,
                                "discord_channel_id": interaction.channel_id,
                                "name": interaction.channel.name,
                            }
                        )
                        result[article_type] = {
                            "article_type": article_type,
                            "is_active": True,
                            "is_channel_change": False,
                            "channel_id": interaction.channel_id
                        }
                    elif existing_channel.is_active and existing_channel.discord_channel_id != interaction.channel_id:
                        # パターン3: 既存設定があり、アクティブだが、異なるチャンネル
                        old_channel_id = existing_channel.discord_channel_id
                        
                        self.guild_channel_dao.update_channel_by_id(
                            existing_channel.id,
                            {
                                "discord_channel_id": interaction.channel_id,
                                "name": interaction.channel.name
                            }
                        )
                        
                        result[article_type] = {
                            "article_type": article_type,
                            "is_active": True,
                            "is_channel_change": True,
                            "channel_id": interaction.channel_id,
                            "old_channel_id": old_channel_id
                        }
                else:
                    # パターン4: コマンドで選択されていない場合
                    result[article_type] = {
                        "article_type": article_type,
                        "is_active": True,
                        "is_channel_change": False,
                        "channel_id": existing_channel.discord_channel_id
                    }
            else:
                # 既存の設定がない場合
                if is_selected:
                    # パターン5: 既存設定がなく、コマンドで選択された
                    new_channel = {
                        "name": interaction.channel.name,
                        "discord_channel_id": interaction.channel_id,
                        "guild_id": interaction.guild_id,
                        "article_type": article_type,
                        "is_active": True
                    }
                    self.guild_channel_dao.insert_channel(new_channel)
                    
                    result[article_type] = {
                        "article_type": article_type,
                        "is_active": True,
                        "is_channel_change": False,
                        "channel_id": interaction.channel_id
                    }
                else:
                    # パターン6: 既存設定がなく、コマンドでも選択されていない
                    result[article_type] = {
                        "article_type": article_type,
                        "is_active": False,
                        "is_stopped": False
                    }
        
        return result
    
    def unregister_channel(self, interaction):
        channels = self.guild_channel_dao.get_by_guild_id(interaction.guild_id)
        result = {}
        all_article_types = [
            ArticleType.LOL_PATCH,
            ArticleType.TFT_PATCH,
            ArticleType.LOL_NEWS,
            ArticleType.TFT_NEWS
        ]

        disabled_channel_id = interaction.channel.id
        
        for article_type in all_article_types:            
            # 既存のチャンネル設定を取得
            existing_channel = None
            for channel in channels:
                if article_type == channel.article_type:
                    existing_channel = channel
                    break
            
            # 処理パターンに応じた分岐
            if existing_channel:
                # 既存の設定がある場合
                if existing_channel.discord_channel_id == disabled_channel_id:
                    # 設定されていたチャンネルで/stopを実行された場合
                    if existing_channel.is_active is True:
                        # パターン1: 既存設定があり、アクティブで、停止対象
                        self.guild_channel_dao.update_channel_by_id(
                            existing_channel.id,
                            {
                                "is_active": False
                            }
                        )
                        result[article_type] = {
                            "article_type": article_type,
                            "is_active": False,
                            "is_stopped": True
                        }
                    else:
                        # パターン2: 既存設定があり、停止対象だがすでにアクティブでない
                        result[article_type] = {
                            "article_type": article_type,
                            "is_active": False,
                            "is_stopped": False
                        }
                else:
                    # パターン3: 停止対象外
                    result[article_type] = {
                        "article_type": article_type,
                        "is_active": existing_channel.is_active,
                        "is_channel_change": False,
                        "is_stopped": False
                    }
            else:
                # パターン4: 既存設定がない
                result[article_type] = {
                    "article_type": article_type,
                    "is_active": False,
                    "is_stopped": False
                }
        
        return result
    
    def fetch_current_status(self, interaction):
        channels = self.guild_channel_dao.get_by_guild_id(interaction.guild_id)
        result = {}
        all_article_types = [
            ArticleType.LOL_PATCH,
            ArticleType.TFT_PATCH,
            ArticleType.LOL_NEWS,
            ArticleType.TFT_NEWS
        ]
        
        for article_type in all_article_types:            
            # 既存のチャンネル設定を取得
            existing_channel = None
            for channel in channels:
                if article_type == channel.article_type:
                    existing_channel = channel
                    break
            
            # 処理パターンに応じた分岐
            if existing_channel:
                result[article_type] = {
                    "article_type": article_type,
                    "is_active": existing_channel.is_active,
                    "is_channel_change": False,
                    "is_stopped": False
                }
            else:
                result[article_type] = {
                    "article_type": article_type,
                    "is_active": False,
                    "is_stopped": False
                }
        
        return result
