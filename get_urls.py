from html import entities
import json
import requests
import pprint
import time
from get_models import session_setup

session = session_setup()


def main():
    url = "https://api.sketchfab.com/v3/models?archives_flavours=false&cursor=bz0yNA%3D%3D&downloadable=true&user=ffishAsia-and-floraZia"
    next_flag = True
    print(url)
    models_info = []
    while next_flag:
        result = session.request(method="GET", url=url)
        time.sleep(1)
        response = result.json()
        # ここでレスポンスを色々処理しよう
        urls, uids, names = get_model_info(response)
        entry = [
            {"url": v[0], "uid": v[1], "name": v[2]} for v in zip(urls, uids, names)
        ]
        models_info.extend(entry)
        # pprint.pprint(entry)
        # save_file(lines=urls, name="urls")
        # save_file(lines=uids, name="uids")

        # サーチページの続きを読み込む
        next_url = response["next"]
        print(next_url)
        if next_url == ("" or None):
            next_flag = False
            continue
        url = next_url
    # pprint.pprint(result.json())
    with open("urls.json", "w") as f:
        json.dump(models_info, f, ensure_ascii=False)


def get_model_info(response: dict):
    # レスポンスから検索結果に含まれるモデルのURLを取得する
    results: list[dict] = response["results"]
    urls = []
    uids = []
    names = []
    for result in results:
        url = result["uri"]
        uid = result["uid"]
        name = result["name"]
        urls.append(url)
        uids.append(uid)
        names.append(name)
    return urls, uids, names


def save_file(lines: list, name: str):
    # ファイルを作成する
    f = open(f"{name}.txt", "a")
    for line in lines:
        f.write(line + "\n")
    f.close()


main()
