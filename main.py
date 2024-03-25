import aiohttp
import discord
import io
import json
import os
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from urllib.parse import urljoin
from keep_alive import keep_alive
from google.cloud import storage


global intents
global TOKEN
global client
global PREFIX
global bot
global bucket_name
global bucket
global patch_title_json_path
global dev_title_json_path
global guild_list_json_path
global channel_id

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

keep_alive()
TOKEN = os.environ["DISCORD_BOT_TOKEN"]
client = storage.Client.from_service_account_json("sacred-epigram-411001-8bba796e9384.json")
PREFIX = "!"  # コマンドプリフィックス
bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), intents=intents)

bucket_name = 'loljp-discord-bot'
bucket = client.get_bucket(bucket_name)
patch_title_json_path = 'last_patch_title.json'
dev_title_json_path = 'last_dev_title.json'
guild_list_json_path = 'guild_list.json'

# channel_id = 1155455630585376858 # announce
channel_id = 1199592409525399653 # dev

# GCS上のjsonファイルからサーバーリストを取得する
def load_guild_list():
    global guild_list

    blob = bucket.blob(guild_list_json_path)
    content = blob.download_as_text()
    data = json.loads(content)
    guild_list = data

# GCS上のjsonファイルから直近の更新内容を取得する
def load_last_titles(json_path):
    blob = bucket.blob(json_path)
    content = blob.download_as_text()

    data = json.loads(content)
    if json_path == patch_title_json_path:
        data = data.get("last_patch_title", "")
    return data


# GCS上のjsonファイルにサーバーリストを保存する
def save_guild_list():
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

def make_channel_id_list():
    channel_id_list = [entry["channel_id"] for entry in guild_list]

@bot.event
async def on_ready():
    print(f"{bot.user}のログインに成功！")
    check_patch_title.start()
    check_dev_title.start()
    load_guild_list()

@bot.event
async def on_guild_join(guild):
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
    save_guild_list()

@bot.event
async def on_guild_remove(guild):
    guild_list = [item for item in guild_list if item.get('guild_id') != guild.id]
    save_guild_list()

@bot.command()
async def start(ctx):
    old_channel_name = None
    message = None
    result = False
    channel_duplicate = False
    for element in guild_list:
        if element["guild_id"] == ctx.guild.id:
            if element["channel_id"] == ctx.channel.id:
                result = True
                channel_duplicate = True
                break
            if not element["channel_name"] is None:
                old_channel_name = element["channel_name"]
            element["channel_name"] = ctx.channel.name
            element["channel_id"] = ctx.channel.id
            element["is_enabled"] = True
            result = True
            save_guild_list()

    if not result:
        message = f"`!start`コマンドの実行に失敗しました。\nbotをサーバーから削除し、再度追加することで改善されるかもしれません。\n詳しくは開発者にお問い合わせください。"
    elif channel_duplicate:
        message = f"`!start`コマンドは以前にこのチャンネルで実行されています。\nお知らせを送信するチャンネルを変更するには別のチャンネルで`!start`コマンドを実行してください。"
    elif old_channel_name is None:
        message = f"`!start`コマンドが実行されました！\n次回から ***{ctx.channel.name}*** チャンネルで更新をお知らせします！\nお知らせを停止するには`!stop`コマンドを実行してください。"
    else:
        message = f"`!start`コマンドが実行されました！\n更新をお知らせするチャンネルを ***{old_channel_name}*** チャンネルから ***{ctx.channel.name}*** チャンネルに変更します！"
    
    await ctx.send(message)

@bot.command()
async def stop(ctx):
    old_channel_name = None
    message = None
    result = False
    wrong_channel = False
    for element in guild_list:
        if element["guild_id"] == ctx.guild.id:
            if not element["channel_id"] == ctx.channel.id:
                result = True
                wrong_channel = True
                old_channel_name = element["channel_name"]
                break
            element["channel_name"] = None
            element["channel_id"] = None
            element["is_enabled"] = False
            result = True
            save_guild_list()

    if not result:
        message = f"`!stop`コマンドの実行に失敗しました。\n開発者にお問い合わせください。"
    elif wrong_channel:
        message = f"`!stop`コマンドは更新お知らせを行っているチャンネルで実行してください。\n現在更新をお知らせしているチャンネルは ***{old_channel_name}*** チャンネルです。"
    else:
        message = f"`!stop`コマンドが実行されました。\n更新お知らせを終了します。\nお知らせを再開するには任意のチャンネルで`!start`コマンドを実行してください。"
        
    await ctx.send(message)

@tasks.loop(minutes=15)
async def check_patch_title():
    if not is_defined(last_patch_title):
        last_patch_title = load_last_titles(patch_title_json_path)

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
        patch_url = first_target_a_tag.get("href")
        patch_full_url = urljoin(url, patch_url)

        # full_url のリンク先ページを取得
        async with aiohttp.ClientSession() as session:
            async with session.get(patch_full_url) as response:
                page_html = await response.text()

        # "Patch-Highlights_TW_1920x1080_JA.jpgを含む画像URLを取得
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

        # <h2>要素を取得
        h2_element = first_target_a_tag.find(
            "h2", class_="style__Title-sc-1h41bzo-8 hvOSAW"
        )

        patch_title = h2_element.text

        if patch_title != last_patch_title:
            channel = bot.get_channel(channel_id)  # パッチ情報を送信するチャンネルのIDを指定

            if img_url is not None:
                # 画像ファイルのURLから画像をダウンロード
                async with aiohttp.ClientSession() as session:
                    async with session.get(img_url) as image_response:
                        image_data = await image_response.read()

                # 画像をメッセージに添付して送信
                image_file = discord.File(
                    io.BytesIO(image_data), filename="patch_hilight_image.png"
                )
                await channel.send(
                    f"### - [{patch_title}](<{patch_full_url}>)", file=image_file
                )
            else:
                await channel.send(f"### - [{patch_title}](<{patch_full_url}>)")

            title_json = {"last_patch_title": patch_title}
            # 新しいパッチタイトルをファイルに保存
            save_last_titles(title_json, patch_title_json_path)

@check_patch_title.before_loop
async def before_check_patch_title():
    await bot.wait_until_ready()

@tasks.loop(minutes=15)
async def check_dev_title():
    if not is_defined(last_dev_titles):
        last_dev_titles = load_last_titles(dev_title_json_path)
    
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

    titles = {}
    for target_a_tag in target_a_tags:
        dev_url = target_a_tag.get("href")
        dev_full_url = urljoin(url, dev_url)

        # <h2>要素を取得
        h2_element = target_a_tag.find("h2", class_="style__Title-sc-1h41bzo-8 hvOSAW")

        titles[h2_element.text] = dev_full_url

    for key, value in titles.items():
        if key not in last_dev_titles:
            print("Dev titles were updated")
            channel = bot.get_channel(channel_id)
            # メッセージを送信
            await channel.send(f"### - [{key}]({value})")
            # last_dev_titlesの末尾にtitleを追加
            last_dev_titles_list = list(last_dev_titles.items())
            last_dev_titles_list.append((key, value))

            if len(last_dev_titles_list) > 20:
                last_dev_titles_list = last_dev_titles_list[-20:]

            # 辞書に変換して保存
            title_json = dict(last_dev_titles_list)
            save_last_titles(title_json, dev_title_json_path)

@check_dev_title.before_loop
async def before_check_dev_title():
    await bot.wait_until_ready()

# 変数が定義されているか
def is_defined(variable_name):
    return variable_name in globals() or variable_name in locals()

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"An error occurred: {e}")
    os.system("kill 1")
