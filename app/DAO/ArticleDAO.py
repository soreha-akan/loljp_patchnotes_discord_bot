
from config.dependencies import Article
from DAO.BaseDAO import BaseDAO

class ArticleDAO(BaseDAO):
    def insert_article(self, title: str, article_type: int, url: str):
        new_article = Article(
            title=title,
            article_type=article_type,
            url=url,
        )
        self.insert(new_article)
        return new_article
    
    def exists_by_url(self, url: str) -> bool:
        return self.query(Article).filter(
            Article.url == url,
            Article.deleted == False
        ).first() is not None
    
    def fetch_latest_article(self, article_type: int):
        return self.query(Article).filter(
            Article.article_type == article_type,
            Article.deleted == False
        ).order_by(Article.created_at.desc()).first()
    
    def get_unposted_articles(self):
        return self.query(Article).filter(
            Article.deleted == False,
            Article.is_posted == False,
        ).all()
    
    def mark_articles_as_posted(self, articles: list[Article]):
        article_ids = [article.id for article in articles]
        self.update(
            Article,
            [Article.id.in_(article_ids)],
            {Article.is_posted: True}
        )
