from Models.Guild import Guild
from config.database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from utils.time import jst_now

class GuildDAO:
    def __init__(self):
        self.db: Session = SessionLocal()

    def get_by_guild_id(self, guild_id: int):
        return self.db.query(Guild).filter(Guild.guild_id == guild_id).first()

    def update_by_conditions(self, conditions: dict, values: dict) -> int:
        """
            任意の条件と更新値でレコードを更新する。

            Parameters:
                conditions (dict): 例 {Guild.guild_id: 1234567890}
                values (dict): 例 {Guild.deleted: False, Guild.deleted_at: None}

            Returns:
                int: 更新された行数
        """
        query = self.db.query(Guild)
        for col, val in conditions.items():
            query = query.filter(col == val)

        result = query.update(values, synchronize_session=False)
        self.db.commit()

        return result 

    def insert_guild(self, guild_id: int, name: str):
        new_guild = Guild(
            guild_id=guild_id,
            name=name,
        )
        self.db.add(new_guild)
        self.db.commit()
        self.db.refresh(new_guild)

        return new_guild

    def soft_delete_by_guild_id(self, guild_id: int) -> int:
        """
            指定のguild_idと一致するレコードを論理削除する。

            Parameters:
                guild_id

            Returns:
                int: 削除された行数
        """
        result = self.db.query(Guild).filter(Guild.guild_id == guild_id).update({
            "deleted": True,
            "deleted_at": jst_now
        })
        self.db.commit()

        return result