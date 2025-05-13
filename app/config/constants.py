from enum import IntEnum


class ArticleType(IntEnum):
    LOL_PATCH = 1
    TFT_PATCH = 2
    LOL_NEWS = 3
    TFT_NEWS = 4

ARTICLE_TYPE_NAMES: dict[ArticleType, str] = {
    ArticleType.LOL_PATCH: "LoLパッチノート",
    ArticleType.TFT_PATCH: "TFTパッチノート",
    ArticleType.LOL_NEWS: "LoL公式ニュース記事",
    ArticleType.TFT_NEWS: "TFT公式ニュース記事",
}

class CommandName():
    START = "/start"
    STOP = "/stop"
    STATUS = "/status"
    TEST = "/test"
    HELP = "/help"

class RiotURL():
    LOL_PATCH = "https://www.leagueoflegends.com/ja-jp/news/tags/patch-notes/"
    LOL_NEWS = "https://www.leagueoflegends.com/ja-jp/news/"
    TFT_NEWS = "https://teamfighttactics.leagueoflegends.com/ja-jp/news/"

class Domain():
    LOL = "leagueoflegends.com"
    TFT = "teamfighttactics.leagueoflegends.com"
    YT = "www.youtube.com"

class YTChannelName():
    LOL_JP = "リーグ・オブ・レジェンド"
    LOL = "League of Legends"
    TFT_JP = "Teamfight Tactics - Japan"
    TFT = "Teamfight Tactics"
    LOL_ESPORTS_JP = "LoL Esports JP"
    LOL_ESPORTS = "LoL Esports"

class ChannelStatus(str):
    MOVED = "moved"
    NEW = "new"
    NO_CHANGE = "no_change"