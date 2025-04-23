from Models.GuildChannel import GuildChannel
from config.database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from Models.Guild import Guild
from utils.time import jst_now

class GuildChannelDAO:
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def get_active_channels(self, article_type):
        return self.db.query(GuildChannel).join(Guild).filter(
            Guild.deleted == False,
            GuildChannel.is_active == True,
            GuildChannel.article_type == article_type
        ).all()
    
    def update_channel_by_id(self, id, values: dict):
        self.db.query(GuildChannel).filter(
            GuildChannel.id == id
        ).update(values)
        self.db.commit()
    
    def insert_channel(self, new_channel):
        self.db.add(new_channel)
        self.db.commit()
    
    def get_by_guild_id(self, guild_id):
        return self.db.query(GuildChannel).filter(
            GuildChannel.deleted == False,
            GuildChannel.guild_id == guild_id
        ).all()

    def soft_delete_by_guild_id(self, guild_id: int) -> int:
        """
            指定のguild_idと一致するレコードを論理削除する。

            Parameters:
                guild_id

            Returns:
                int: 削除された行数
        """
        result = self.db.query(GuildChannel).filter(
            GuildChannel.guild_id == guild_id,
            GuildChannel.deleted == False
        ).update({
            "deleted": True,
            "deleted_at": jst_now
        })
        self.db.commit()

        return result