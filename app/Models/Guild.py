from sqlalchemy import Column, Integer, String, Numeric, Boolean, TIMESTAMP, func, BigInteger
from sqlalchemy.orm import relationship
from config.database import Base
from utils.time import jst_now

class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    guild_id = Column(BigInteger, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, default=jst_now)
    modified_at = Column(TIMESTAMP, default=jst_now, onupdate=jst_now)
    deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(TIMESTAMP, nullable=True)

    # 関連付け: NotificationSettingテーブルと関連付け
    notification_settings = relationship("NotificationSetting", back_populates="guild")