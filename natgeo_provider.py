#!/usr/bin/python3
import os
from helper import fetch_and_parse
from retry_deco import retry


@retry(tries=10, delay=10)
def fetch_url():
    base_url = "http://www.nationalgeographic.com/photography/photo-of-the-day/"
    pattern = "<meta\s+property=\"og:image\"\s+content=\"(.*?)\".*/>"
    url = fetch_and_parse(base_url, pattern)
    return url, os.path.basename(url)


if __name__ == "__main__":
    print(fetch_url())
