## 実装したい機能
### 実装予定
* とりあえずコード整理！メンテしにくすぎ！
* 発信するChannelの指定
* 記事の更新を検知するAPI的な部分とチャット送信する部分は分けた方がいいかも？
* パッチノートの更新検知
  page-data.jsonの比較でいけるか？あまりにでかいけど
  更新時にpage-data.jsonのresult.data.all.nodes[0].patch_notes_body.patchnotesをjson保存して比較するか
* 必要なLog収集
* 処理のトランザクション化
* Authorを取得して表示
  
  Class style__Author-sc-1h41bzo-11 dYVbdC

  authorない場合もあるのでif文でTrueのときのみ
* class分割する
* https://lolesports.com/news
  * フィルター　動画
  * dev update除外
* devのjsonの並び順が文字列順になってるっぽい？
* jsonをメモリ上に呼び出していないとき（インスタンスが開始してからjsonを一度も呼んでない）> undefinedのときのみjsonの呼び出しを行う
* Prime削除
* コマンドリスト作成
* コマンド 開始（チャンネル変更もここ） ストップ 

### 複数サーバー対応
* メッセージの作成と送信を分ける
* メッセージの送信では複数チャンネルIDをforで回す

### 実装済み
* _辞書型でデータ作って更新履歴管理_
  * 20件までjsonに保存
  * 取得した最新6件をfor文で一件ずつjsonのデータと比較
  * 比較して不一致があった場合はメッセージ送信 jsonの末尾に追加
  * jsonの件数が20件以上になったら保存する前にjsonの添字0のデータを削除

### ボツ
* 画面共有させることはできるか → できない
* https://www.leagueoflegends.com/ja-jp/news/tags/patch-notes/ のように、PrimeGamingの記事のみを羅列するルーティングが存在するのか？RiotGamesJPに聞いてみる > PrimeGamingが終わった