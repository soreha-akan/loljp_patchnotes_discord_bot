## 実装したい機能
### 実装予定
* とりあえずコード整理！メンテしにくすぎ！
* 発信するChannelの指定
* 記事の更新を検知するAPI的な部分とチャット送信する部分は分けた方がいいかも？
* 必要なLog収集
* Authorを取得して表示
* パッチノートの更新検知
  
  Class style__Author-sc-1h41bzo-11 dYVbdC

  authorない場合もあるのでif文でTrueのときのみ
* file分割する
* https://www.leagueoflegends.com/ja-jp/news/tags/patch-notes/ のように、PrimeGamingの記事のみを羅列するルーティングが存在するのか？RiotGamesJPに聞いてみる
* https://lolesports.com/news
  * フィルター　動画
  * dev update除外


### 実装済み
* _辞書型でデータ作って更新履歴管理_
  * 20件までjsonに保存
  * 取得した最新6件をfor文で一件ずつjsonのデータと比較
  * 比較して不一致があった場合はメッセージ送信 jsonの末尾に追加
  * jsonの件数が20件以上になったら保存する前にjsonの添字0のデータを削除

### ボツ
* 画面共有させることはできるか → できない
