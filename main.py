import aiohttp
import discord
import io
import json
import os
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from urllib.parse import urljoin
from keep_alive import keep_alive

class CheckTask:
    def __init__(self, name, url, channel_id):
        self.name = name
        self.url = url
        self.channel_id = channel_id
        self.last_title = ""
        self.task = tasks.loop(minutes=15)(self.check)

    async def check(self, bot):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        target_a_tags = soup.find_all('a', class_='style__Wrapper-sc-1h41bzo-0 style__ResponsiveWrapper-sc-1h41bzo-13 eIUhoC cGAodJ isVisible')

        for a_tag in target_a_tags:
            # <h2>要素を取得
            h2_element = a_tag.find('h2', class_='style__Title-sc-1h41bzo-8 hvOSAW')

            # h2要素のテキストを取得
            title = h2_element.text if h2_element else ""

            # テキスト条件を追加
            if self.should_send_notification(title):
                if title != self.last_title:
                    channel = bot.get_channel(self.channel_id)

                    # メッセージを送信
                    full_url = urljoin(self.url, a_tag.get('href'))
                    await channel.send(f'### - [{title}]({full_url})')
                    self.last_title = title

                    # 新しいタイトルを保存
                    bot.save_last_title(f'last_{self.name}.json', title)
                    break  # 条件を満たす要素が見つかったらループを終了

    def should_send_notification(self, title):
        return True  # ここに通知を送信する条件を追加

class PatchBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        intents = discord.Intents.default()
        intents.typing = False
        intents.presences = False
        intents.message_content = True
        self.bot_token = os.environ.get('DISCORD_BOT_TOKEN')
        self.prefix = '!'  # コマンドプリフィックス
        
        self.check_tasks = [
            CheckTask(
                name="check_patch_title",
                url="https://www.leagueoflegends.com/ja-jp/news/tags/patch-notes/",
                channel_id=1155455630585376858
            ),
            CheckTask(
                name="check_dev_title",
                url="https://www.leagueoflegends.com/ja-jp/news/dev/",
                channel_id=1155455630585376858
            ),
            CheckTask(
                name="check_prime_title",
                url="https://www.leagueoflegends.com/ja-jp/news/community/",
                channel_id=1155455630585376858
            ),
        ]

    def load_last_title(self, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                return data.get('last_title', '')
        except (FileNotFoundError, json.JSONDecodeError):
            return ''

    def save_last_title(self, filename, title):
        with open(filename, 'w') as file:
            json.dump({'last_title': title}, file)

    async def on_ready(self):
        print(f'{self.user}のログインに成功！')
        for task in self.check_tasks:
            task.task.start(self)

    async def on_error(self, event, *args, **kwargs):
        print(f"An error occurred in event {event}: {args}, {kwargs}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

        print(f"An error occurred in command '{ctx.command}': {error}")

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.message_content = True

    bot = PatchBot(command_prefix=commands.when_mentioned_or('!'), intents=intents)  # Botインスタンスを作成
    keep_alive()
    try:
        bot.run(bot.bot_token)
    except Exception as e:
        print(f"An error occurred: {e}")
        os.system("kill 1")