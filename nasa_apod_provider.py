import re
from urllib.parse import urljoin
from urllib.request import urlopen

from retry_deco import retry


@retry(tries=10, delay=10)
def fetch_url():
    url = None
    base_url = "https://apod.nasa.gov/apod"
    pattern = "<a href=\"(image/.*)\""
    regex = re.compile(pattern)

    with urlopen(base_url) as in_f:
        iter = regex.finditer(in_f.read().decode())
        try:
            url = list(iter)[0].group(1)
        except Exception as ignored:
            pass

    return url if url is None else urljoin(base_url, url)


if __name__ == "__main__":
    print(fetch_url())
