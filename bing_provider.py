#!/usr/bin/python3

import json
from urllib import parse as urlparse
from urllib.request import urlopen

from retry_deco import retry


# Fetch today's photo url
@retry(tries=10, delay=10)
def fetch_url():
    json_obj = None
    base_url = "https://www.bing.com"
    json_url = "/HPImageArchive.aspx?format=js&idx=0&n=1"
    with urlopen(urlparse.urljoin(base_url, json_url)) as in_f:
        json_obj = json.loads(in_f.read().decode("UTF-8"))

    url = None if json_obj is None else urlparse.urljoin(base_url, json_obj["images"][0]["url"])
    name = urlparse.parse_qs(urlparse.urlparse(url).query)['id'][0]
    return url, name


if __name__ == "__main__":
    print(fetch_url())
