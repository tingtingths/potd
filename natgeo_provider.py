from helper import fetch_and_parse
from retry_deco import retry


@retry(tries=10, delay=10)
def fetch_url():
    base_url = "http://www.nationalgeographic.com/photography/photo-of-the-day/"
    pattern = "<meta\s+property=\"og:image\"\s+content=\"(.*?)\".*/>"
    return fetch_and_parse(base_url, pattern)


if __name__ == "__main__":
    print(fetch_url())
