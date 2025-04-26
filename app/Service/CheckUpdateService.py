import asyncio
from urllib.parse import urljoin, urlparse, urlunparse
from DAO.GuildDAO import GuildDAO
from DAO.ArticleDAO import ArticleDAO
from Models.Article import Article
from DAO.NotificationSettingDAO import NotificationSettingDAO
from bs4 import BeautifulSoup
from Service.SendMessageService import SendMessageService
from config.constants import ArticleType, RiotURL
import aiohttp

class CheckUpdateService:
    
    def __init__(self, bot):
        self.bot = bot
        self.guild_dao = GuildDAO()
        self.article_dao = ArticleDAO()
        self.send_message_service = SendMessageService(bot)
        self.notification_setting_dao = NotificationSettingDAO()

    async def check_updates(self):
        # 各URLのページを非同期に取得
        page_data = await self.fetch_pages([
            RiotURL.LOL_PATCH, RiotURL.TFT_NEWS, RiotURL.LOL_NEWS
        ])

        # 各ページの更新チェック
        await self.check_LoL_patch_update(page_data[RiotURL.LOL_PATCH])
        await self.check_TFT_patch_update(page_data[RiotURL.TFT_NEWS])
        await self.check_news_update(page_data[RiotURL.TFT_NEWS], ArticleType.TFT_NEWS)
        await self.check_news_update(page_data[RiotURL.LOL_NEWS], ArticleType.LOL_NEWS)

    async def fetch_pages(self, urls):
        """ 複数のURLからページを非同期に取得 """
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_page(session, url) for url in urls]
            pages = await asyncio.gather(*tasks)
        return dict(zip(urls, pages))

    async def fetch_page(self, session, url):
        """ 単一ページを非同期に取得 """
        async with session.get(url) as response:
            html = await response.text()
        return BeautifulSoup(html, "html.parser")

    async def check_LoL_patch_update(self, soup):
        await self.check_patch_update(soup, ArticleType.LOL_PATCH)

    async def check_TFT_patch_update(self, soup):
        await self.check_patch_update(soup, ArticleType.TFT_PATCH)

    async def check_patch_update(self, soup, article_type):
        """ パッチ更新チェックの共通メソッド """
        latest_patch = self.article_dao.fetch_latest_article(article_type)
        patch_title, patch_url = await self.fetch_patch_link_and_title(soup, article_type)
        if patch_title and patch_url:
            normalized_url = self.normalize_url(patch_url)
            if not self.article_dao.exists_by_url(normalized_url) and (not latest_patch or normalized_url != latest_patch.url):
                patch_img = await self.get_patch_img(normalized_url)
                await self.handle_new_article(patch_title, normalized_url, article_type, patch_img)
                new_article = Article(
                    title=patch_title,
                    article_type=article_type,
                    url=normalized_url,
                )
                self.article_dao.insert(new_article)

    async def check_news_update(self, soup, article_type):
        """ ニュース記事更新チェックの共通メソッド """
        news_list = await self.fetch_news_link_list(soup, article_type)
        for news in news_list:
            if article_type == ArticleType.LOL_NEWS:
                print(news)
            url = news["url"]
            title = news["title"]
            normalized_url = self.normalize_url(url)
            if not self.article_dao.exists_by_url(normalized_url):
                await self.handle_new_article(title, normalized_url, article_type)
                new_article = Article(
                    title=title,
                    article_type=article_type,
                    url=normalized_url,
                )
                self.article_dao.insert(new_article)

    async def handle_new_article(self, article_title, article_url, article_type, patch_img=None):
        channels = self.notification_setting_dao.get_active_channels(article_type)
        channel_id_list = [channel.channel_id for channel in channels]
        for channel_id in channel_id_list:
            print(channel_id)
            await self.send_message_service.send_new_article_message(article_title, article_url, article_type, channel_id, patch_img)

    async def fetch_patch_link_and_title(self, soup, article_type):
        """ パッチノートのタイトルとURLを取得 """
        if article_type == ArticleType.LOL_PATCH:
            return await self.fetch_lol_patch_link_and_title(soup)
        elif article_type == ArticleType.TFT_PATCH:
            return await self.fetch_tft_patch_link_and_title(soup)
        return None, None

    async def fetch_lol_patch_link_and_title(self, soup):
        """ LoL パッチノートリンクとタイトルを取得 """
        first_target_a_tag = soup.find_all('a', attrs={'data-testid': 'articlefeaturedcard-component'})[0]
        title_text_element = first_target_a_tag.find("div", attrs={'data-testid': 'card-title'})
        patch_title = title_text_element.text
        href = first_target_a_tag.get("href")
        patch_url = urljoin(RiotURL.LOL_PATCH, href)
        return patch_title, patch_url

    async def fetch_tft_patch_link_and_title(self, soup):
        """ TFT パッチノートリンクとタイトルを取得 """
        patch_title = None
        patch_url = None
        target_a_tags = soup.find_all('a', attrs={'data-testid': 'articlefeaturedcard-component'})
        for target_a_tag in target_a_tags:
            title_text_element = target_a_tag.find("div", attrs={'data-testid': 'card-title'})
            if title_text_element and "パッチノート" in title_text_element.text:
                patch_title = title_text_element.text
                href = target_a_tag.get("href")
                patch_url = urljoin(RiotURL.TFT_NEWS, href)
                break
        return patch_title, patch_url

    async def fetch_news_link_list(self, soup, article_type):
        """ 記事のリンクとタイトルをリストで取得 """
        target_a_tags = soup.find_all('a', attrs={'data-testid': 'articlefeaturedcard-component'})
        articles = []
        for target_a_tag in target_a_tags:
            href = target_a_tag.get("href")
            url = urljoin(RiotURL.LOL_NEWS if article_type == ArticleType.LOL_NEWS else RiotURL.TFT_NEWS, href)
            title_text_element = target_a_tag.find("div", attrs={'data-testid': 'card-title'})
            articles.append({"title": title_text_element.text, "url": url})
        return articles

    async def get_patch_img(self, patch_url):
        """ パッチ画像を取得 """
        async with aiohttp.ClientSession() as session:
            async with session.get(patch_url) as response:
                page_html = await response.text()
        page_soup = BeautifulSoup(page_html, "html.parser")
        img_url = self.extract_img_url(page_soup)
        if img_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(img_url) as image_response:
                    return await image_response.read()
        return None

    def extract_img_url(self, soup):
        """ パッチ画像URLを抽出 """
        header = soup.find("h2", string="パッチハイライト")
        if header:
            content_div = header.find_next("div", class_="content-border")
            if content_div:
                a_tag = content_div.find("a", class_="skins cboxElement", href=True)
                if a_tag:
                    return a_tag["href"]
        candidate_imgs = soup.find_all("a", class_="skins cboxElement", href=True)
        for a in candidate_imgs:
            if "1920x1080" in a["href"]:
                return a["href"]
        if candidate_imgs:
            return candidate_imgs[0]["href"]
        return None

    async def send_test_message(self, guild_id):
        channels = self.notification_setting_dao.get_active_setting(guild_id)

        for channel in channels:
            latest_article = self.article_dao.fetch_latest_article(channel.article_type)

            if latest_article:
                patch_img = None
                if latest_article.article_type in (ArticleType.LOL_PATCH, ArticleType.TFT_PATCH):
                    patch_img = await self.get_patch_img(latest_article.url)
                
                await self.send_message_service.send_new_article_message(latest_article.title, latest_article.url, latest_article.article_type, channel.channel_id, patch_img)

        return len(channels)
                        
    def normalize_url(self, url: str) -> str:
        """URLを正規化する関数

        次の処理を行います：
        1. 前後の空白を削除
        2. パスの末尾のスラッシュを削除
        """
        # URLが空または None の場合はそのまま返す
        if not url:
            return url

        # URLをパース
        parsed = urlparse(url.strip())

        # パスの末尾のスラッシュを削除
        path = parsed.path
        # パスが空文字列の場合はスラッシュ削除しない（ルートパス '/' もそのまま維持）
        if path and path != '/' and path.endswith('/'):
             path = path[:-1]

        # 正規化されたコンポーネントでURLを再構築
        normalized_parts = list(parsed)
        normalized_parts[2] = path

        # URLを再構築して返す
        return urlunparse(tuple(normalized_parts))