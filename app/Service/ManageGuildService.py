from DAO.GuildDAO import GuildDAO
from DAO.NotificationSettingDAO import NotificationSettingDAO
from config.dependencies import Guild, NotificationSetting
from config.constants import ArticleType

class ManageGuildService:
    def __init__(self):
        self.guild_dao = GuildDAO()
        self.notification_setting_dao = NotificationSettingDAO()

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

        self.notification_setting_dao.soft_delete_by_guild_id(guild_id)

        new_settings = [
            NotificationSetting(guild_id=guild_id, article_type=article)
            for article in ArticleType
        ]
        self.notification_setting_dao.bulk_insert(new_settings)

    def handle_guild_remove(self, guild_id: int):
        result = self.guild_dao.soft_delete_by_guild_id(guild_id)
        # Guildに紐付くNotificationSettingを論理削除
        if result:
            self.notification_setting_dao.soft_delete_by_guild_id(guild_id)

    
    def register_channel(self, interaction, selected_article_types):
        settings = self.notification_setting_dao.get_by_guild_id(interaction.guild_id)
        channel_id = interaction.channel.id

        result = {}
        for setting in settings:
            key = ArticleType(setting.article_type)
            result[key] = {
                "is_active": setting.is_active,
                "channel_id": setting.channel_id,
                "is_active_before": setting.is_active,
                "channel_id_before": setting.channel_id,
            }

            if key in selected_article_types:
                self.notification_setting_dao.update_channel_by_id(
                    setting.id,
                    {
                        "is_active": True,
                        "channel_id": channel_id,
                        "channel_name": interaction.channel.name,
                    }
                )
                result[key]["is_active"] = True
                result[key]["channel_id"] = channel_id
            else:
                if setting.channel_id == channel_id and setting.is_active:
                    self.notification_setting_dao.update_channel_by_id(
                        setting.id,
                        {
                            "is_active": False,
                            "channel_id": None,
                            "channel_name": None,
                        }
                    )
                    result[key]["is_active"] = False
                    result[key]["channel_id"] = None

        return result
    
    def unregister_channel(self, interaction):
        is_empty = not self.notification_setting_dao.check_exist_active_setting(interaction.guild_id)
        if is_empty:
            return is_empty
        settings = self.notification_setting_dao.get_by_guild_id(interaction.guild_id)
        disabled_channel_id = interaction.channel.id

        result = {}
        for setting in settings:
            key = ArticleType(setting.article_type)

            result[key] = {
                "is_active": setting.is_active,
                "channel_id": setting.channel_id,
                "is_active_before": setting.is_active,
                "channel_id_before": setting.channel_id,
            }

            if setting.channel_id == disabled_channel_id:
                self.notification_setting_dao.update_channel_by_id(
                    setting.id,
                    {
                        "is_active": False,
                        "channel_id": None,
                        "channel_name": None,
                    }
                )
                result[key]["is_active"] = False
                result[key]["channel_id"] = None

        return result
    
    def fetch_current_status(self, interaction):
        settings = self.notification_setting_dao.get_by_guild_id(interaction.guild_id)

        result = {}
        for setting in settings:
            key = ArticleType(setting.article_type)

            result[key] = {
                "is_active": setting.is_active,
                "channel_id": setting.channel_id,
                "is_active_before": False,
                "channel_id_before": None,
            }

        return result
    
    def fetch_status_by_channel(self, interaction):
        settings = self.notification_setting_dao.get_by_channel_id(interaction.guild_id, interaction.channel.id)

        result = {}
        for setting in settings:
            key = ArticleType(setting.article_type)

            result[key] = {
                "is_active": setting.is_active,
                "channel_id": setting.channel_id,
                "is_active_before": False,
                "channel_id_before": None,
            }

        return result
