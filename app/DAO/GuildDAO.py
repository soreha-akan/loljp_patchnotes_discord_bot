
from config.dependencies import Guild
from utils.time import jst_now
from DAO.BaseDAO import BaseDAO

class GuildDAO(BaseDAO):
    def get_by_guild_id(self, guild_id: int):
        return self.query(Guild).filter(Guild.guild_id == guild_id).first()

    def update_by_conditions(self, conditions: dict, values: dict) -> int:
        query = self.query(Guild)
        for col, val in conditions.items():
            query = query.filter(col == val)

        result = query.update(values, synchronize_session=False)
        self.commit()
        return result 

    def insert_guild(self, guild_id: int, name: str):
        new_guild = Guild(
            guild_id=guild_id,
            name=name,
        )
        self.insert(new_guild)
        return new_guild

    def soft_delete_by_guild_id(self, guild_id: int) -> int:
        result = self.query(Guild).filter(Guild.guild_id == guild_id).update({
            "deleted": True,
            "deleted_at": jst_now()
        })
        self.commit()
        return result