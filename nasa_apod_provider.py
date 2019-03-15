#!/usr/bin/python3
import os
from helper import fetch_and_parse
from retry_deco import retry


@retry(tries=10, delay=10)
def fetch_url():
    base_url = "https://apod.nasa.gov/apod"
    pattern = "<a href=\"(image/.*)\""
    url = fetch_and_parse(base_url, pattern)
    return url, os.path.basename(url)


if __name__ == "__main__":
    print(fetch_url())
