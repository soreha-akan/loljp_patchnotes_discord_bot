import discord
import io
from config.constants import ArticleType
from DAO.GuildDAO import GuildDAO
from DAO.ArticleDAO import ArticleDAO
from DAO.GuildChannelDAO import GuildChannelDAO

class SendMessageService:
    def __init__(self, bot):
        self.bot = bot
        self.guild_dao = GuildDAO()
        self.article_dao = ArticleDAO()
        self.guild_channel_dao = GuildChannelDAO()

    async def send_new_article_message(self, article_title, article_url, article_type, channel_id, patch_img):
        channel = self.bot.get_channel(channel_id)
        if patch_img is not None and article_type in (ArticleType.LOL_PATCH, ArticleType.TFT_PATCH):
            image_file = discord.File(
                io.BytesIO(patch_img), filename="patch_hilight_image.png"
            )
            await channel.send(
                f"### - [{article_title}](<{article_url}>)", file=image_file
            )
        else:
            await channel.send(f"### - [{article_title}](<{article_url}>)")

    