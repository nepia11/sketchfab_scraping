import requests
import pprint
import time


def main():
    url = "https://api.sketchfab.com/v3/search?type=models&user=ffishAsia-and-floraZia&downloadable=true&archives_flavors=false"
    next_flag = True
    print(url)
    while next_flag:
        result = requests.get(url)
        time.sleep(1)
        response = result.json()
        # ここでレスポンスを色々処理しよう
        urls, uids = get_model_urls(response)
        save_file(lines=urls, name="urls")
        save_file(lines=uids, name="uids")

        # サーチページの続きを読み込む
        next_url = response["next"]
        print(next_url)
        if next_url == ("" or None):
            next_flag = False
            continue
        url = next_url
    # pprint.pprint(result.json())


def get_model_urls(response: dict):
    # レスポンスから検索結果に含まれるモデルのURLを取得する
    results: list[dict] = response["results"]
    urls = []
    uids = []
    for result in results:
        url = result["uri"]
        uid = result["uid"]
        urls.append(url)
        uids.append(uid)
    return urls, uids


def save_file(lines: list, name: str):
    # ファイルを作成する
    f = open(f"{name}.txt", "a")
    for line in lines:
        f.write(line + "\n")
    f.close()


main()
