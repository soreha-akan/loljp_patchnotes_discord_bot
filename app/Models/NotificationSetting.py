from sqlalchemy import Column, Integer, String, Numeric, SmallInteger, Boolean, TIMESTAMP, func, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from config.database import Base
from utils.time import jst_now


class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String(100), nullable=True)
    channel_id = Column(BigInteger, nullable=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id"), nullable=False)
    article_type = Column(SmallInteger, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, default=jst_now)
    modified_at = Column(TIMESTAMP, default=jst_now, onupdate=jst_now)
    deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(TIMESTAMP, nullable=True)

    guild = relationship("Guild", back_populates="notification_settings")