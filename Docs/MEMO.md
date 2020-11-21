
## 開発メモ

### 機能要件
- アカウント追加を楽にする
- DB10000行制限対策
- 一日のメニュー数拡大
- 矢印間違えて押しちゃう
- 自分に！しか送られないことを周知
- マニュアル整備（改行できるとかしらんでしょっていう）
- タイム一覧見やすく メニューがわかりにくい？
- User.roleにVIEWERを設ければ応答はするけど編集はできない人、みたいなのが作れる（引退したらそうするか？）
- メニュー削除時に削除予定のレコード数も通知する
- ボタン押したらフォームに入力される
- noun のクレジットどっかに書く
- エンドポイントをwebhookに変更
- DestructiveUpdateが必要なくなったけど、この代替を理解しているか
- Excelも同時に送りつけたら？
- リレーの名前もスタイル扱いすれば可能


### フロントエンド
- 今後に合わせてモダンな設計に合わせるのもありか
- Sass、Vueには手を出せる SPAは難しいか
- webpack？勉強しなきゃ JS圧縮はしてもいい
- TypescriptはJSのスーパーセットなんやーーー
- [Vuetify](https://vuetifyjs.com/en/)割と美しいから使ってみたい
- Flaskからの移行はORMこれ使ってる以上難しいか → 次回チャレンジ
フロントエンド静的ならFlaskよりもAPIに特化したフレームワークを使うべきじゃ？

- Lambdaに移行させることあるかなあ
- このフォルダ構成だとルーティングに苦労した
application.pyのFlaskインスタンス作成時にディレクトリを指定してある。
あまり理解できていないが`http://127.0.0.1:5000/static/js/menu.js`にアクセスできればCSSやJSが適応される
HTMLファイル上では`src="../static/js/menu.js"`て指定してある

- JinjaもVueも二重括弧を使うから競合する
Jinjaが先にサーバーで処理するためJinjaが優先される
[こちら](https://blog.hysakhr.com/2019/09/14/flaskjinja2-vue-js-%E3%81%A7mustache%E8%A8%98%E6%B3%95-%E3%81%AE%E8%A1%9D%E7%AA%81%E5%9B%9E%E9%81%BF/)を参考にVueのデリミタを['${', '}']に修正して解決

- スマホでClickイベントの感覚が非常に悪かったためtouchedイベントでもトリガーするように
[preventを使う必要性](https://am-yu.net/2019/02/12/vue-js-mousedown-touchstart/)

- コンポーネント内のフォームの値と親での値を動機させるのに詰まった
emitや二重v-modelで解決
[【Vue.js】コンポーネントの親子関係はInputを作って学べ](https://b1tblog.com/2019/10/03/vue-input/)
[公式Doc:子コンポーネントのイベントを購読する](https://jp.vuejs.org/v2/guide/components.html#%E5%AD%90%E3%82%B3%E3%83%B3%E3%83%9D%E3%83%BC%E3%83%8D%E3%83%B3%E3%83%88%E3%81%AE%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88%E3%82%92%E8%B3%BC%E8%AA%AD%E3%81%99%E3%82%8B)
[Vue.jsで、親コンポーネントからもらった変数を子コンポーネントで更新したいときの対処法](https://qiita.com/masatomix/items/ab4f0488083554f5fceb)
> コンポーネント側でmodelとバインドさせるのは引数valueで固定、と書いてあるがcontentという引数名でも動いた...

- <script src="https://cdn.jsdelivr.net/npm/vue"></script>
<script src="https://cdn.jsdelivr.net/npm/vue@2.6.12"></script>
<script src="https://cdn.jsdelivr.net/npm/vue@2.6.10/dist/vue.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vue@2.6.12/dist/vue.min.js"></script>
これなにが違うねん...



### データベース(ローカルの話)
- Postgresのバージョンは12.4
- 接続は`psql -d database -U user `
- timのロールを生成 パスワードも適当に設定 `alter role login`とかでログイン権限付与できる
- データベースの初期設定
```
create database tim encoding = UTF8
LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' template = template0
```
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

- ORM使うのはどうなんだろうか（吐き出すSQLの確認は後ほど必要）
> オーバーヘッドが大きいなら生SQL書く可能性も
> SQLインジェクション防ぐためにプリペアドステートメントを使わなくては

- 旧DBだとセル内の区切り文字にカンマを使っているせいでCSVにしたときにわかりにくかった
REPLACE関数を使うことで解決
`SELECT keyid, date, sequence, replace(swimmer, ',', '_'), replace(times, ',', '_'), replace(styles, ',', '_') from record ORDER BY keyid;`

- `nextval('records_recordid_seq')`を指定してINSERTした行じゃないと、シーケンス関数の初期値が1のままになってしまう
select setval('records_recordid_seq', 300)などを実行してシーケンスを進める


### LINE API
- 本来ならWebhookを受け取ったら[署名を検証](https://developers.line.biz/ja/reference/messaging-api/#signature-validation)するけど面倒くさいからしない
- ローカルでデバッグ環境を整えたおかげで開発が爆速になった。ローカルホストに実際と同じPOSTデータを送る。そんでアカウントにプッシュメッセージを飛ばす
- LIFFのURLに追加のパスやパラメータを設定するとリダイレクトされる ＝ 二回ロードされるけど問題なく使用可能
- テキストエリアを可変にさせるには別のタグ使うってのもあり
- Flexの容量をsys.getsizeofを使って知ることはできないか→大きければ警告
- なぜかbutton以外のFlex要素にaction-labelを指定しても受信できない→dataに指定するしかない
- 空白文字は送れない →半角スペースを送ることで対応


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

- [設定関係ドキュメント](https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/config.html)
FLASK_ENVを環境変数で指定することで自動でDEBUGモードをオンにしてくれる

- Procfileを以下のように修正したけど
```
web: gunicorn application:app --pythonpath app
```
TiM直下のrun.pyから起動させないことでimportの参照とかずれたりしないのかな


### その他
- データ容量大丈夫か再検証する必要 具体的にいくつのメニューが送れるか タイムもいくつまでか
- collectionやitertools使えばもっと高速にできるか
- メールの添付ファイルは文字コード指定なしでもスマホなら問題ないが、Excelで開くと文字化けしてしまう
> 'utf-8-sig'で指定するとExcel側もUTF8として認識してくれる。これはBOM付きUTF8

- 二段階認証をONにしているGMAILアカウントでは、アカウントパスワードではなくアプリパスワードで接続する
[参考:アプリパスワードについて](https://gammasoft.jp/support/prepare-gmail-account/)
[参考:Gmailヘルプ](https://support.google.com/mail/answer/7126229?hl=ja)
[参考:Python-SMTPライブラリ](https://docs.python.org/ja/3/library/smtplib.html)
> SMTP_SSL インスタンスは SMTP と全く同じように動作します。SMTP_SSL は、接続の始めからSSLが必要であり、 starttls() が適切でない状況で使用するべきです。 host が指定されていない場合、ローカルホストが使用されます。 port が0の場合、標準のSMTP-over-SSLポート（465）が使用されます。

- 画像データやり取りするとユーザー外で使うのに可哀想
- [Atomパッケージ](https://complesso.jp/593/)
