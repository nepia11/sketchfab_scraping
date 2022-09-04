from urllib.parse import urlparse
import requests
import pprint
import time
import os
import requests_cache
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests_ratelimiter import LimiterAdapter
from dotenv import load_dotenv
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin


class CachedLimiterSession(CacheMixin, LimiterMixin, requests.Session):
    """Session class with caching and rate-limiting behavior. Accepts arguments for both
    LimiterSession and CachedSession.
    """


# Optionally use Redis as both the bucket backend and the cache backend
session = CachedLimiterSession(
    "session_cache",
    per_minute=300 / 60,
)

# token setup
load_dotenv()
api_token = os.environ["API_TOKEN"]
cwd = os.path.dirname(__file__)
download_type = os.environ["DOWNLOAD_TYPE"]

# setup session
retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    respect_retry_after_header=True,
)
session.mount("https://", HTTPAdapter(max_retries=retries))
session.mount("http://", HTTPAdapter(max_retries=retries))


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
    result = session.get(url, headers=headers)
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


def create_resumed_urls(urls: list):
    # urlsからdownloadedなものを除去してresumed_urlsを作成
    resumed_urls = []
    for url in urls:
        r = session.request(method="GET", url=url)
        r_json = r.json()
        name = r_json.get("name", None)
        if not is_downloaded_file(name):
            resumed_urls.append(url)

    return resumed_urls


def read_urls(filename: str):
    f = open(os.path.join(cwd, filename), "r")
    urls = [v.rstrip("\n") for v in f.readlines()]
    return urls


def write_resumed_urls():
    urls = read_urls("urls.txt")
    resumed_urls = create_resumed_urls(urls)
    save_file(resumed_urls, "resumed_urls")


def main(urls: list[str]):
    models_path = mkdir_models()

    for i, url in enumerate(urls):
        print(i)
        if url == ("" or None):
            continue
        try:
            # 名前を取得
            if session.cache.has_url(url=url, method="GET"):
                print(f"Request cached:{url}")

            r = session.request(method="GET", url=url)
            time.sleep(0.1)

            r_json = r.json()
            name = r_json.get("name", None)

            if name is not None:
                print(name)
            else:
                print(r.headers)

            # ダウンロード済みならスキップする
            if is_downloaded_file(name):
                print("skipping download")
                continue
            time.sleep(2)

            # ダウンロードリンクを取得
            download_url = get_download_url(url)
            if download_url is None:
                print(f"not found download url {name}. skipping download")
                continue
            filepath = download(download_url, models_path, name)
            save_file([filepath], "downloaded")
            print(f"✅ downloaded:{filepath}")
            # time_count(5)
            time.sleep(1)

        except Exception as e:
            print(e)
            continue


# time_count(60 * 60)
urls = create_resumed_urls(read_urls("urls.txt"))
main(urls)
# write_resumed_urls()
