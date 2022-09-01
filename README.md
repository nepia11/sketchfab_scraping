## 説明

sketchfab からモデルを一括でダウンロードするスクリプト

対象はベタ書きしてるので必要に応じて書き換えれば他にも使えるかも

pipenv について

- https://zenn.dev/nekoallergy/articles/py-env-pipenv01
- https://pipenv-ja.readthedocs.io/ja/translate-ja/

## セットアップ

推奨は pipenv をインストールしてプロジェクトディレクトリで`pipenv install`

上記が終わったら`pipenv shell`

### pipenv 以外の場合

`pip install -r requirements.txt` で必要なパッケージをインストールする

## 使い方

- cmd とか terminal とかの作業ディレクトリをこのプロジェクトがあるディレクトリに移動する
- urls.txt を取得していなければ、`python get_urls.py`を実行する
  - urls.txt が作成されて中身が書き込まれていれば成功
- `get_models.py`の`api_token`に自分の sketchfab の api トークンを記入する
  - https://sketchfab.com/settings/password
  - ここから取得できる
- `python get_models.py`を実行する
  - 途中で実行が中断しても、再度実行すればダウンロードが終わったところから再開してくれるはず
  - コード中の`download_type`を書き換えれば別のファイルタイプでダウンロードできるはず
