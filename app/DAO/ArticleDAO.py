from Models.Article import Article
from config.database import SessionLocal
from sqlalchemy.orm import Session
from config.constants import ArticleType

class ArticleDAO:
    def __init__(self):
        self.db: Session = SessionLocal()

        
    def insert_article(self, title: str, url: str, article_type: int):
        new_article = Article(
            title=title,
            article_type=article_type,
            url=url,
        )
        self.db.add(new_article)
        self.db.commit()
        self.db.refresh(new_article)

        return new_article
    
    def exists_by_url(self, url: str) -> bool:
        return self.db.query(Article.id).filter(
            Article.url == url,
            Article.deleted == False
        ).first() is not None
    
    def fetch_latest_article(self, article_type: int):
        return self.db.query(Article).filter(
            Article.article_type == article_type,
            Article.deleted == False
        ).order_by(Article.created_at.desc()).first()

