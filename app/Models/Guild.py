from sqlalchemy import Column, Integer, String, Numeric, Boolean, TIMESTAMP, func
from sqlalchemy.orm import relationship
from config.database import Base
from app.utils.time import jst_now

class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    guild_id = Column(Numeric(30), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, default=jst_now)
    modified_at = Column(TIMESTAMP, default=jst_now, onupdate=jst_now)
    deleted = Column(Boolean, nullable=True, default=False)
    deleted_at = Column(TIMESTAMP, nullable=True)

    # 関連付け: GuildChannelテーブルと関連付け
    channels = relationship("GuildChannel", back_populates="guild")