## 実装したい機能
### Hotfix!!!!
* チャンネルで発言権限がない場合に機能が停止しているためExceptionを作る
* guild_listに追加するロジックをstartコマンドにも仕込む

### Feature
* 機能別
  * LoL PatchNote
  * TFT PatchNote
  * Articles
    * dev
    * lol eSports video
    * https://www.leagueoflegends.com/ja-jp/news/game-updates/
    * https://www.leagueoflegends.com/ja-jp/news/media/
    * https://www.leagueoflegends.com/ja-jp/news/lore/
    * https://www.leagueoflegends.com/ja-jp/news/community/
    * https://www.leagueoflegends.com/ja-jp/news/riot-games/
  * LoLEsports news (公式のeSportsNewsとのダブりチェックはしない)
  * TaskLoopを機能ごとではなくひとまとめで行う（1タスクで順番に行うことでurlのダブりを防ぐ狙い）
    * TaskLoopは一個だけ、その一個で各機能を回す

### 実装予定
* パッチノートの更新検知
  page-data.jsonの比較でいけるか？あまりにでかいけど
  更新時にpage-data.jsonのresult.data.all.nodes[0].patch_notes_body.patchnotesをjson保存して比較するか
* 必要なLog収集
* 処理のトランザクション化
* Authorを取得して表示
  
  Class style__Author-sc-1h41bzo-11 dYVbdC

  authorない場合もあるのでif文でTrueのときのみ
* class分割する
* Statusコマンドでチャンネルの権限をチェック
* Startコマンド実行時にチャンネルの権限を確認して自分がメッセージ送信できない場合はアラートを出し、チャンネルID登録を行わない
  * テキストチャンネルの権限を変更し自らの発言を許可する  

### 実装済み
* _辞書型でデータ作って更新履歴管理_
  * 20件までjsonに保存
  * 取得した最新6件をfor文で一件ずつjsonのデータと比較
  * 比較して不一致があった場合はメッセージ送信 jsonの末尾に追加
  * jsonの件数が20件以上になったら保存する前にjsonの添字0のデータを削除

### ボツ
* 画面共有させることはできるか → できない
* https://www.leagueoflegends.com/ja-jp/news/tags/patch-notes/ のように、PrimeGamingの記事のみを羅列するルーティングが存在するのか？RiotGamesJPに聞いてみる > PrimeGamingが終わった