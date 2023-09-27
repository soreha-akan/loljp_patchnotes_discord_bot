import aiohttp
import discord
import io
import json
import os
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from urllib.parse import urljoin
from keep_alive import keep_alive


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

# ファイルから最後の/devタイトルを読み取る
def load_last_dev_title():
    try:
        with open('last_dev_title.json', 'r') as file:
            data = json.load(file)
            return data.get('last_dev_title', '')
    except (FileNotFoundError, json.JSONDecodeError):
        return ''

# ファイルに最後の/devタイトルを保存
def save_last_dev_title(title):
    with open('last_dev_title.json', 'w') as file:
        json.dump({'last_dev_title': title}, file)

last_patch_title = load_last_patch_title()
last_dev_title = load_last_dev_title()

@bot.event
async def on_ready():
    print(f'{bot.user}のログインに成功！')
    check_patch_title.start()
    check_dev_title.start()

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
        patch_full_url = urljoin(url, patch_url)
        
        # full_url のリンク先ページを取得
        async with aiohttp.ClientSession() as session:
            async with session.get(patch_full_url) as response:
                page_html = await response.text()
        
        # "skins cboxElement" クラスを持つ最初の <a> 要素を取得し、そのURLを取得
        page_soup = BeautifulSoup(page_html, 'html.parser')
        patch_hilight_image = page_soup.find('a', class_='skins cboxElement')
        
        # <h2>要素を取得
        h2_element = first_target_a_tag.find('h2', class_='style__Title-sc-1h41bzo-8 hvOSAW')
        
        patch_title = h2_element.text
        
        if patch_title != last_patch_title:
            channel = bot.get_channel(1155455630585376858)  # パッチ情報を送信するチャンネルのIDを指定

           # 画像ファイルのURLから画像をダウンロード
            async with aiohttp.ClientSession() as session:
                async with session.get(patch_hilight_image['href']) as image_response:
                    image_data = await image_response.read()
                  
            # 画像をメッセージに添付して送信
            image_file = discord.File(io.BytesIO(image_data), filename='patch_hilight_image.png')
            await channel.send(f'### - [{patch_title}](<{patch_full_url}>)', file=image_file)
            last_patch_title = patch_title
            
            # 新しいパッチタイトルをファイルに保存
            save_last_patch_title(patch_title)

@check_patch_title.before_loop
async def before_check_patch_title():
    await bot.wait_until_ready()

@tasks.loop(minutes=15)
async def check_dev_title():
    global last_dev_title
    
    url = "https://www.leagueoflegends.com/ja-jp/news/dev/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
    
    soup = BeautifulSoup(html, 'html.parser')
    target_a_tags = soup.find_all('a', class_='style__Wrapper-sc-1h41bzo-0 style__ResponsiveWrapper-sc-1h41bzo-13 eIUhoC cGAodJ isVisible')

    if target_a_tags:
        first_target_a_tag = target_a_tags[0]
        dev_url = first_target_a_tag.get('href')
        dev_full_url = urljoin(url, dev_url)
         
        # <h2>要素を取得
        h2_element = first_target_a_tag.find('h2', class_='style__Title-sc-1h41bzo-8 hvOSAW')
        
        dev_title = h2_element.text
        
        if dev_title != last_dev_title:
            channel = bot.get_channel(1155455630585376858)  # /dev情報を送信するチャンネルのIDを指定
           
            # 画像をメッセージに添付して送信
            await channel.send(f'### - [{dev_title}]({dev_full_url})')
            last_dev_title = dev_title
            
            # 新しいパッチタイトルをファイルに保存
            save_last_dev_title(dev_title)

@check_dev_title.before_loop
async def before_check_dev_title():
    await bot.wait_until_ready()

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"An error occurred: {e}")
    os.system("kill 1")
