from config.dependencies import Guild, NotificationSetting
from utils.time import jst_now
from DAO.BaseDAO import BaseDAO

class NotificationSettingDAO(BaseDAO):
    def get_active_channels(self, article_type):
        return self.query(NotificationSetting).join(Guild).filter(
            Guild.deleted == False,
            NotificationSetting.deleted == False,
            NotificationSetting.is_active == True,
            NotificationSetting.article_type == article_type
        ).all()
    
    def update_channel_by_id(self, id, values: dict):
        self.update(NotificationSetting, [NotificationSetting.id == id], values)
    
    def update_by_channel_id(self, channel_id, values: dict):
        self.update(NotificationSetting, [NotificationSetting.channel_id == channel_id, NotificationSetting.deleted == False], values)
            
    def check_exist_active_setting(self, guild_id) -> bool:
        return self.query(NotificationSetting).filter(
            NotificationSetting.is_active == True,
            NotificationSetting.guild_id == guild_id
        ).first() is not None
    
    def get_by_guild_id(self, guild_id):
        return self.query(NotificationSetting).filter(
            NotificationSetting.deleted == False,
            NotificationSetting.guild_id == guild_id
        ).order_by(NotificationSetting.article_type.asc()).all()
    
    def get_active_setting(self, guild_id):
        return self.query(NotificationSetting).filter(
            NotificationSetting.deleted == False,
            NotificationSetting.guild_id == guild_id,
            NotificationSetting.is_active == True,
        ).order_by(NotificationSetting.article_type.asc()).all()
    
    def get_by_channel_id(self, guild_id, channel_id):
        return self.query(NotificationSetting).filter(
            NotificationSetting.deleted == False,
            NotificationSetting.guild_id == guild_id,
            NotificationSetting.channel_id == channel_id,
        ).order_by(NotificationSetting.article_type.asc()).all()

    def soft_delete_by_guild_id(self, guild_id: int) -> int:
        result = self.query(NotificationSetting).filter(
            NotificationSetting.guild_id == guild_id,
            NotificationSetting.deleted == False
        ).update({
            "deleted": True,
            "deleted_at": jst_now()
        })
        self.commit()
        return result