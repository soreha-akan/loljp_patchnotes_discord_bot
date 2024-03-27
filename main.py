import aiohttp
import discord
import io
import json
import os
import pytz
from bs4 import BeautifulSoup
from datetime import datetime
from discord import Intents, Client
from discord.app_commands import CommandTree
from discord.ext import tasks
from urllib.parse import urljoin
from keep_alive import keep_alive
from google.cloud import storage

jst = pytz.timezone('Asia/Tokyo')

intents = Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

keep_alive()
TOKEN = os.environ["DISCORD_BOT_TOKEN"]
storage_client = storage.Client.from_service_account_json("sacred-epigram-411001-8bba796e9384.json")
bot = Client(intents=intents)
tree = CommandTree(bot)

bucket_name = 'loljp-discord-bot'
bucket = storage_client.get_bucket(bucket_name)
patch_info_json_path = 'product/last_patch_info.json'
dev_info_json_path = 'product/recent_dev_info.json'
guild_list_json_path = 'product/guild_list.json'

is_develop = False
if is_develop:
    patch_info_json_path = 'develop/last_patch_info.json'
    dev_info_json_path = 'develop/recent_dev_info.json'
    guild_list_json_path = 'develop/guild_list.json'

# GCS上のjsonファイルからサーバーリストを取得する
def load_guild_list():
    blob = bucket.blob(guild_list_json_path)
    content = blob.download_as_text()
    data = json.loads(content)
    return data

# GCS上のjsonファイルから直近の更新内容を取得する
def load_last_info_json(json_path):
    blob = bucket.blob(json_path)
    content = blob.download_as_text()

    return json.loads(content)

# GCS上のjsonファイルにサーバーリストを保存する
def save_guild_list(guild_list):
    content = json.dumps(
    guild_list,
    ensure_ascii=False,
    indent=2,
    sort_keys=True,
    separators=(",", ": "),
    )

    blob = bucket.blob(guild_list_json_path)
    blob.upload_from_string(content, content_type="application/json")

# GCS上のjsonファイルに直近の更新内容を保存する
def save_last_titles(titles, json_path):
    content = json.dumps(
    titles,
    ensure_ascii=False,
    indent=2,
    sort_keys=True,
    separators=(",", ": "),
    )

    blob = bucket.blob(json_path)
    blob.upload_from_string(content, content_type="application/json")

def get_enabled_channel_id_list(guild_list):
    enabled_channel_list = []
    for element in guild_list:
        if element["is_enabled"]:
            enabled_channel_list.append(element["channel_id"])
    return enabled_channel_list
    
@bot.event
async def on_ready():
    print(f"{bot.user}のログインに成功！")
    check_patch_update.start()
    check_dev_update.start()
    await tree.sync()

@bot.event
async def on_guild_join(guild):
    guild_list = load_guild_list()
    for item in guild_list:
        if "guild_id" in item and item["guild_id"] == guild.id:
            return

    new_guild_info = {
        "guild_name": guild.name,
        "guild_id": guild.id,
        "channel_name": None,
        "channel_id": None,
        "is_enabled": False
    }

    guild_list.append(new_guild_info)
    save_guild_list(guild_list)

@bot.event
async def on_guild_remove(guild):
    guild_list = load_guild_list()
    new_guild_list = [item for item in guild_list if item.get('guild_id') != guild.id]
    save_guild_list(new_guild_list)

@tree.command(name='start', description='更新のお知らせを開始します。') 
async def start_command(ctx): 
    guild_list = load_guild_list()
    old_channel_id = None
    message = None
    result = False
    channel_duplicate = False
    for element in guild_list:
        if element["guild_id"] == ctx.guild.id:
            if element["channel_id"] == ctx.channel.id:
                result = True
                channel_duplicate = True
                break
            if not element["channel_id"] is None:
                old_channel_id = element["channel_id"]
            element["channel_name"] = ctx.channel.name
            element["channel_id"] = ctx.channel.id
            element["is_enabled"] = True
            result = True
            save_guild_list(guild_list)

    base_channel_url = 'https://discord.com/channels/' + str(ctx.guild.id) + '/'
    current_channel_url = base_channel_url + str(ctx.channel.id)
    old_channel_url = base_channel_url + str(old_channel_id)

    if not result:
        message = f"`/start`コマンドの実行に失敗しました。\nbotをサーバーから削除し、再度追加することで改善されるかもしれません。\n詳しくは開発者にお問い合わせください。"
    elif channel_duplicate:
        message = f"`/start`コマンドは以前にこのチャンネルで実行されています。\nお知らせを送信するチャンネルを変更するには別のチャンネルで`/start`コマンドを実行してください。"
    elif old_channel_id is None:
        message = f"`/start`コマンドが実行されました！\n次回から {current_channel_url} チャンネルで更新をお知らせします！\nお知らせを停止するには`/stop`コマンドを実行してください。"
    else:
        message = f"`/start`コマンドが実行されました！\n更新をお知らせするチャンネルを {old_channel_url} チャンネルから {current_channel_url} チャンネルに変更します！"
    
    await ctx.response.send_message(message)

@tree.command(name='stop', description='更新のお知らせを停止します。')
async def stop_command(ctx):
    guild_list = load_guild_list()
    current_channel_id = None
    message = None
    result = False
    already_stop = None
    wrong_channel = False
    for element in guild_list:
        if element["guild_id"] == ctx.guild.id:
            if not element["is_enabled"]:
                result = True
                already_stop = True
                break
            if not element["channel_id"] == ctx.channel.id:
                result = True
                wrong_channel = True
                current_channel_id = element["channel_id"]
                break
            element["channel_name"] = None
            element["channel_id"] = None
            element["is_enabled"] = False
            result = True
            save_guild_list(guild_list)

    base_channel_url = 'https://discord.com/channels/' + str(ctx.guild.id) + '/'
    current_channel_url = base_channel_url + str(current_channel_id)

    if not result:
        message = f"`/stop`コマンドの実行に失敗しました。\n開発者にお問い合わせください。"
    elif already_stop:
        message = f"更新通知は現在有効ではありません。\n`/stop`コマンドは実行されませんでした。"
    elif wrong_channel:
        message = f"`/stop`コマンドは更新お知らせを行っているチャンネルで実行してください。\n現在更新をお知らせしているチャンネルは {current_channel_url} チャンネルです。"
    else:
        message = f"`/stop`コマンドが実行されました。\n更新お知らせを終了します。\nお知らせを再開するには任意のチャンネルで`/start`コマンドを実行してください。"
        
    await ctx.response.send_message(message)

@tree.command(name='status', description='botの稼働状況を表示します。') 
async def start_command(ctx): 
    guild_list = load_guild_list()
    message = None
    result = False
    current_channel_id = None
    is_enabled = None
    for element in guild_list:
        if element["guild_id"] == ctx.guild.id:
            current_channel_id = element["channel_id"]
            is_enabled = element["is_enabled"]
            result = True

    base_channel_url = 'https://discord.com/channels/' + str(ctx.guild.id) + '/'
    current_channel_url = base_channel_url + str(current_channel_id)

    if not result:
        message = f"`/status`コマンドの実行に失敗しました。\n開発者にお問い合わせください。"
    elif is_enabled:
        message = f"更新通知は現在有効になっています。\nお知らせを送信するチャンネルは {current_channel_url} チャンネルです。"
    else:
        message = f"更新通知は現在無効になっています。\n有効にするには任意のチャンネルで`/start`コマンドを実行してください。"
    
    await ctx.response.send_message(message)

@tree.command(name='help', description='コマンドの一覧を表示します。') 
async def start_command(ctx): 
    message = f"`/start`\nコマンドを使用したチャンネルで更新通知を有効にします。\nすでに他のチャンネルで更新通知を利用している場合、発信するチャンネルを変更します。\n\n"
    message += f"`/stop`\n更新通知を無効にします。\n更新通知が行われているチャンネルでのみ使用可能です。\n\n"
    message += f"`/status`\nbotの稼働状況と更新通知が行われるチャンネルを確認できます。\n\n"
    message += f"`/help`\nコマンドの一覧を表示します。（現在あなたが読んでいるものです。）"
    
    await ctx.response.send_message(message)

@tasks.loop(minutes=15)
async def check_patch_update():
    last_patch_info_json = load_last_info_json(patch_info_json_path)
    last_patch_title = last_patch_info_json["title"]
    last_patch_url = last_patch_info_json["url"]

    patch_title, patch_url = await scrape_patch_link_list()

    if patch_title != last_patch_title and patch_url != last_patch_url:
        patch_img = await get_patch_img(patch_url)
        if patch_img is not None:
            # 画像をメッセージに添付して送信
            await send_patch_message(patch_title, patch_url, patch_img)
        else:
            await send_patch_message(patch_title, patch_url)

        new_patch_info_json = {
            "title": patch_title,
            "url": patch_url,
            "modified": datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")
        }
        # 新しいパッチ情報をファイルに保存
        save_last_titles(new_patch_info_json, patch_info_json_path)

async def scrape_patch_link_list():
    print(f"{bot.user} - パッチタイトルチェック開始")
    url = "https://www.leagueoflegends.com/ja-jp/news/tags/patch-notes/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    target_a_tags = soup.find_all(
        "a",
        class_="style__Wrapper-sc-1h41bzo-0 style__ResponsiveWrapper-sc-1h41bzo-13 eIUhoC cGAodJ isVisible",
    )

    if target_a_tags:
        first_target_a_tag = target_a_tags[0]
        h2_element = first_target_a_tag.find(
            "h2", class_="style__Title-sc-1h41bzo-8 hvOSAW"
        )

        patch_title = h2_element.text
        href = first_target_a_tag.get("href")
        patch_url = urljoin(url, href)

        return patch_title, patch_url

async def get_patch_img(patch_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(patch_url) as response:
                page_html = await response.text()

        page_soup = BeautifulSoup(page_html, "html.parser")

        img_tags = page_soup.find_all("img", src=True)
        target_src = "Patch-Highlights_TW_1920x1080_JA"
        match_string_img = [img["src"] for img in img_tags if target_src in img["src"]]
        cbox_class_img = page_soup.find("a", class_="skins cboxElement")

        img_url = None
        if match_string_img:
            img_url = match_string_img[0]
        elif cbox_class_img:
            img_url = cbox_class_img["href"]

        image_data = None
        if img_url is not None:
            async with aiohttp.ClientSession() as session:
                async with session.get(img_url) as image_response:
                    image_data = await image_response.read()

        return image_data

async def send_patch_message(patch_title, patch_url, patch_img=None):
    guild_list = load_guild_list()
    enabled_channel_list = get_enabled_channel_id_list(guild_list)
    if patch_img is not None:
        for channel_id in enabled_channel_list:
            channel = bot.get_channel(channel_id)   
            image_file = discord.File(
                io.BytesIO(patch_img), filename="patch_hilight_image.png"
            )
            await channel.send(
                f"### - [{patch_title}](<{patch_url}>)", file=image_file
            )
    else:
        for channel_id in enabled_channel_list:
            channel = bot.get_channel(channel_id)
            await channel.send(f"### - [{patch_title}](<{patch_url}>)")
        
@check_patch_update.before_loop
async def before_check_patch_update():
    await bot.wait_until_ready()

@tasks.loop(minutes=15)
async def check_dev_update():
    recent_dev_info = load_last_info_json(dev_info_json_path)

    new_dev_info_list = []
    articles = await scrape_dev_link_list()
    for article in articles:
        if check_dev_is_new(article, recent_dev_info):
            new_dev_info = {
                "title": article["title"],
                "url": article["url"],
                "modified": datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")
            }
            new_dev_info_list.append(new_dev_info)
    if len(new_dev_info_list) > 0:
        await send_dev_message(new_dev_info_list)
                
        # recent_dev_infoの末尾にtitleを追加
        recent_dev_info = new_dev_info_list + recent_dev_info
        if len(recent_dev_info) > 20:
            recent_dev_info = recent_dev_info[:20]

        save_last_titles(recent_dev_info, dev_info_json_path)

async def scrape_dev_link_list():
    print(f"{bot.user} - Devタイトルチェック開始")
    url = "https://www.leagueoflegends.com/ja-jp/news/dev/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    target_a_tags = soup.find_all(
        "a",
        class_="style__Wrapper-sc-1h41bzo-0 style__ResponsiveWrapper-sc-1h41bzo-13 eIUhoC cGAodJ isVisible",
    )

    articles = []
    for target_a_tag in target_a_tags:
        href = target_a_tag.get("href")
        dev_url = urljoin(url, href)

        # <h2>要素を取得
        h2_element = target_a_tag.find("h2", class_="style__Title-sc-1h41bzo-8 hvOSAW")

        article = {
            "title": h2_element.text,
            "url": dev_url
        }
        articles.append(article)

    return articles

def check_dev_is_new(article, recent_dev_info):
    for dev_info in recent_dev_info:
        if article["url"] == dev_info["url"]:
            return False
    return True

async def send_dev_message(new_dev_info_list):
    guild_list = load_guild_list()
    enabled_channel_list = get_enabled_channel_id_list(guild_list)
    for new_dev_info in new_dev_info_list:
        for channel_id in enabled_channel_list:
            channel = bot.get_channel(channel_id)
            await channel.send(f"### - [{new_dev_info['title']}]({new_dev_info['url']})")
                
@check_dev_update.before_loop
async def before_check_dev_update():
    await bot.wait_until_ready()

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"An error occurred: {e}")
    os.system("kill 1")
