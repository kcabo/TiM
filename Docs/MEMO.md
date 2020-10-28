
## 開発メモ

### 機能要件
- アカウント追加を楽にする
- DB10000行制限対策
- 一日のメニュー数拡大
- 矢印間違えて押しちゃう
- 自分に！しか送られないことを周知
- マニュアル整備（改行できるとかしらんでしょっていう）
- タイム一覧見やすく メニューがわかりにくい？
- EDITとはなんぞや →日本語にするぞ
- User.roleにVIEWERを設ければ応答はするけど編集はできない人、みたいなのが作れる（引退したらそうするか？）
- メニュー削除時に削除予定のレコード数も通知する
- ボタン押したらフォームに入力される
- noun のクレジットどっかに書く
- hiredis使う
- エンドポイントをwebhookに変更
- DestructiveUpdateが必要なくなったけど、この代替を理解しているか


### フロントエンド
- 今後に合わせてモダンな設計に合わせるのもありか
- Sass、Vueには手を出せる SPAは難しいか
- webpack？勉強しなきゃ JS圧縮はしてもいい
- TypescriptはJSのスーパーセットなんやーーー
- [Vuetify](https://vuetifyjs.com/en/)割と美しいから使ってみたい
- Flaskからの移行はORMこれ使ってる以上難しいか → 次回チャレンジ
- Lambdaに移行させることあるかなあ

### データベース(ローカルの話)
- Postgresのバージョンは12.4
- 接続は`psql -d database -U user `
- timのロールを生成 パスワードも適当に設定 `alter role login`とかでログイン権限付与できる
- ```
create database tim encoding = UTF8
LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' template = template0
```
でデータベースを生成
- エンコーディング、ロケールの値はそれぞれherokuで設定されるのと同値
- `postgresql://tim:0000@localhost:5432/tim`でアクセスする。
- テーブル情報をダンプするやり方がある。そのSQLを発行すればcreate_all()実行しなくていい
- 旧データをCSVにダンプして、ローカルからそのデータを新DBに読み込ませることができるはず
- 文字列の前にE（小文字でもOK）を入力することで改行コードを挿入できる。
> INSERT INTO target_table (target_col) VALUES (E'foo\nbar');
> キーボードから入力できない文字を文字列の中で表したい場合や、特別な意味を持つ文字を入力したい場合、PostgreSQL ではエスケープ文字列を使用します。エスケープ文字列はシングルクォーテーションの前に E または e を記述します。
```
¥b      バックスペース文字
¥f      改ページ
¥n      改行
¥r      復帰改行
¥t      タブ文字
¥o      8進数バイト値
¥xh     16進数バイト値
¥uxxxx  16もしくは32ビットの16進数 Unicode 文字値
```

- ハイフンとアットマークをエスケープする必要がある。ちなみにシングルクォーテーションはどうなんだろ
- `tim=> \i sample.sql`でSQLを読み込めて実行できた
> しかし日本語を含むファイルでは`psql:add_menu.sql:310: ERROR:  符号化方式"SJIS"においてバイト列0xef 0xbdである文字は符号化方式"UTF8"で等価な文字を持ちません`でエラーとなる
> `\encoding UTF8;`をファイル冒頭に挟むことで解決
> しかしやはりPSで日本語の行を読み込むとエラーになる
> コンソール側も`$ chcp 65001`を設定することで解決。普段はSJIS(CP932)だと思われる


### LINE API
- 本来ならWebhookを受け取ったら[署名を検証](https://developers.line.biz/ja/reference/messaging-api/#signature-validation)するけど面倒くさいからしない
- ローカルでデバッグ環境を整えたおかげで開発が爆速になった。ローカルホストに実際と同じPOSTデータを送る。そんでアカウントにプッシュメッセージを飛ばす
- LIFFのURLに追加のパスやパラメータを設定するとリダイレクトされる ＝ 二回ロードされるけど問題なく使用可能
- テキストエリアを可変にさせるには別のタグ使うってのもあり
- Flexの容量をsys.getsizeofを使って知ることはできないか→大きければ警告
- なぜかbuttonではないFlex要素のactionオブジェクトにlabelを指定しても受信できない→dataに指定するしかない
- 空白文字は送れない

### Webサーバ
- 本番環境はGunicorn（WSGIサーバ）
- Gunicornはデフォルトで？マルチワーカー対応かも（LINEのドキュメントではメッセージは非同期で処理してくださいと書いてある）
- Gunicornの引数でアプリの実体位置を指定できる？[pythonpath](https://docs.gunicorn.org/en/latest/settings.html#pythonpath)
- Heroku側の設定でもワーカーの数を指定できたはず
- なおローカルにはGunicornをインストールしていない
- ローカルではAnacondaで管理している
> おかげで？pip freezeの出力が他と違う
> `pip list --format=freeze` で解決した。
> できたリストにGunicorn付け足すのを忘れずに
> 上記コマンドで`setuptools==50.3.0.post20201006`が生成されるが、これはエラーになるため、`.post`以降を削除
> conda list --exportなんていうコマンドもある
> また、conda install できない場合はpipする前に`conda install -c conda-forge`するらしい

- Procfileを以下のように修正したけど
```
web: gunicorn application:app --pythonpath app
```
TiM直下のrun.pyから起動させないことでimportの参照とかずれたりしないのかな


### その他
- データ容量大丈夫か再検証する必要 具体的にいくつのメニューが送れるか タイムもいくつまでか
- メールの文字コードにハマった話
