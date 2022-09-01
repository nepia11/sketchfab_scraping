from urllib.parse import urlparse
import requests
import pprint
import time
import os

api_token = "お前のトークンを入力"
cwd = os.path.dirname(__file__)
download_type = "gltf"
# download_type = "glb"
# download_type = "usdz"


def time_count(t: int):
    print("")
    while t > 0:
        print(f"{t} \r", end="")
        time.sleep(1)
        t -= 1


def mkdir_models():
    print(cwd)
    models_dir_path = os.path.join(cwd, "models")
    if not os.path.exists(models_dir_path):
        os.mkdir(models_dir_path)
    return models_dir_path


def auth_request(url):
    headers = {"Authorization": f"Token {api_token}"}
    result = requests.get(url, headers=headers)
    return result


def get_download_url(url):
    response = auth_request(url + "/download")
    r_json = response.json()
    # print(r_json)
    # download_typeに一致するタイプがなかったら別のタイプにフォールバックする
    main_download_type = set(download_type)
    download_types = set(["gltf", "glb", "usdz"]) - main_download_type
    download_url = r_json.get(download_type, None)
    if download_url is None:
        download_url = r_json.get(download_types.pop(), None)
    if download_url is None:
        download_url = r_json.get(download_types.pop(), None)
    # なかったらない
    if isinstance(download_url, dict):
        download_url = download_url.get("url", None)
    else:
        return None
    return download_url


def download(url: str, download_directory: str, filename: str):
    response = requests.get(url, stream=True)
    url_path = urlparse(url).path
    filepath = os.path.basename(url_path)
    path, ext = os.path.splitext(filepath)
    filepath = os.path.join(download_directory, filename + ext)
    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
            f.flush()
    return filepath


def save_file(lines: list, name: str):
    # ファイルを作成する
    f = open(f"{name}.txt", "a")
    for line in lines:
        f.write(line + "\n")
    f.close()


def is_downloaded_file(name: str):
    filepath = os.path.join(cwd, "downloaded.txt")
    if not os.path.exists(filepath):
        return False
    f = open(filepath, "r")
    text = f.read()
    result = name in text
    f.close()
    return result


def main():
    models_path = mkdir_models()
    # url = "https://api.sketchfab.com/v3/models/7975cbf2d2684533848511efa2c00fda"
    # urlリストのファイルを読み込む
    f = open(os.path.join(cwd, "urls.txt"), "r")
    urls = [v.rstrip("\n") for v in f.readlines()]

    for url in urls:
        if url == ("" or None):
            continue
        try:
            # 名前を取得
            r = auth_request(url)
            r_json = r.json()
            name = r_json["name"]
            print(name)
            # ダウンロード済みならスキップする
            if is_downloaded_file(name):
                print("skipping download")
                time.sleep(0.5)
                continue
            time.sleep(0.5)
            # ダウンロードリンクを取得
            download_url = get_download_url(url)
            if download_url is None:
                print(f"not found download url {name}. skipping download")
                continue
            filepath = download(download_url, models_path, name)
            save_file([filepath], "downloaded")
            print(f"✅ downloaded:{filepath}")
            time_count(5)
        except Exception as e:
            print(e)
            continue


main()
