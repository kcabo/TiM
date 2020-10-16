# 開発メモ

## データベース(ローカルの話)
- Postgresのバージョンは12.4
- timのロールを生成 パスワードも適当に設定 ```alter role login```とかでログイン権限付与できる
- ```create database tim encoding = UTF8 LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' template = template0``` でデータベースを生成
- エンコーディング、ロケールの値はそれぞれherokuで設定されるのと同値
- ```postgresql://tim:0000@localhost:5432/tim```でアクセスする。
