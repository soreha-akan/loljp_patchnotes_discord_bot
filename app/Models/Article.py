from sqlalchemy import Column, Integer, String, SmallInteger, Boolean, TIMESTAMP, func
from config.database import Base
from app.utils.time import jst_now

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    article_type = Column(SmallInteger, nullable=False)
    url = Column(String(2048), nullable=False)
    created_at = Column(TIMESTAMP, default=jst_now)
    modified_at = Column(TIMESTAMP, default=jst_now, onupdate=jst_now)
    deleted = Column(Boolean, nullable=True, default=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
