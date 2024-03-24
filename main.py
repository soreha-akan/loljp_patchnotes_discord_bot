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
patch_title_json_path = 'last-update-json/last_patch_title.json'
dev_title_json_path = 'last-update-json/last_dev_title.json'

channel_id = 1155455630585376858 # announce
# channel_id = 1199592409525399653 # dev



# GCS上のjsonファイルから直近の更新内容を取得する
def load_last_titles(json_path):
    blob = bucket.blob(json_path)
    content = blob.download_as_text()

    data = json.loads(content)
    if json_path == patch_title_json_path:
        data = data.get("last_patch_title", "")
    return data

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

@bot.event
async def on_ready():
    print(f"{bot.user}のログインに成功！")
    check_patch_title.start()
    check_dev_title.start()

@tasks.loop(minutes=15)
async def check_patch_title():
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

try:
    bot.run(TOKEN)
except Exception as e:
    print(f"An error occurred: {e}")
    os.system("kill 1")
