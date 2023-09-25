from keep_alive import keep_alive
import discord
import os
from discord.ext import commands, tasks
import aiohttp
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

keep_alive()
TOKEN = os.environ['DISCORD_BOT_TOKEN']
PREFIX = '!'  # コマンドプリフィックス

bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), intents=intents)

# ファイルから最後のパッチタイトルを読み取る
def load_last_patch_title():
    try:
        with open('last_patch_title.json', 'r') as file:
            data = json.load(file)
            return data.get('last_patch_title', '')
    except (FileNotFoundError, json.JSONDecodeError):
        return ''

# ファイルに最後のパッチタイトルを保存
def save_last_patch_title(title):
    with open('last_patch_title.json', 'w') as file:
        json.dump({'last_patch_title': title}, file)

last_patch_title = load_last_patch_title()

@bot.event
async def on_ready():
    print(f'{bot.user}のログインに成功！')
    check_patch_title.start()

@tasks.loop(minutes=15)
async def check_patch_title():
    global last_patch_title
    
    url = "https://www.leagueoflegends.com/ja-jp/news/tags/patch-notes/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
    
    soup = BeautifulSoup(html, 'html.parser')
    target_a_tags = soup.find_all('a', class_='style__Wrapper-sc-1h41bzo-0 style__ResponsiveWrapper-sc-1h41bzo-13 eIUhoC cGAodJ isVisible')

    if target_a_tags:
        first_target_a_tag = target_a_tags[0]
        patch_url = first_target_a_tag.get('href')
        full_url = urljoin(url, patch_url)
        
        # <h2>要素を取得
        h2_element = first_target_a_tag.find('h2', class_='style__Title-sc-1h41bzo-8 hvOSAW')
        
        if h2_element:
            patch_title = h2_element.text
        else:
            patch_title = 'パッチノート'
        
        if patch_title != last_patch_title:
            channel = bot.get_channel(1155455630585376858)  # パッチ情報を送信するチャンネルのIDを指定
            await channel.send(f'[{patch_title}]({full_url})')
            last_patch_title = patch_title
            
            # 新しいパッチタイトルをファイルに保存
            save_last_patch_title(patch_title)

@check_patch_title.before_loop
async def before_check_patch_title():
    await bot.wait_until_ready()

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"An error occurred: {e}")
    os.system("kill 1")
