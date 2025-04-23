from sqlalchemy import Column, Integer, String, Numeric, SmallInteger, Boolean, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from app.utils.time import jst_now


class GuildChannel(Base):
    __tablename__ = "guild_channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    discord_channel_id = Column(Numeric(30), nullable=True)
    guild_id = Column(Integer, ForeignKey("guilds.guild_id"), nullable=False)
    article_type = Column(SmallInteger, nullable=False)
    is_active = Column(Boolean, nullable=True, default=True)
    created_at = Column(TIMESTAMP, default=jst_now)
    modified_at = Column(TIMESTAMP, default=jst_now, onupdate=jst_now)
    deleted = Column(Boolean, nullable=True, default=False)
    deleted_at = Column(TIMESTAMP, nullable=True)

    guild = relationship("Guild", back_populates="channels")

    def __repr__(self):
        return f"<GuildChannel(id={self.id}, name={self.name}, article_type={self.article_type})>"
