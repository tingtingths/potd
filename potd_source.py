import json
import os
import re
from abc import ABC, abstractmethod
from urllib.parse import urlparse, urljoin, parse_qs
from urllib.request import urlopen

from config import log
from retry_deco import retry


class POTDSource(ABC):

    @abstractmethod
    def image_url(self) -> (str, str):
        pass

    @abstractmethod
    def fetch_image(self) -> (bytes, str):
        pass

    def _fetch_and_parse(self, base_url, pattern):
        url = None
        regex = re.compile(pattern)

        with urlopen(base_url, timeout=5) as in_f:
            charset = in_f.headers.get_content_charset()
            iter = regex.finditer(in_f.read().decode("utf-8" if charset is None else charset))
            try:
                url = list(iter)[0].group(1)
            except Exception as ignored:
                pass

        return url if url is None else urljoin(base_url, url)

    def _fetch(self, url):
        log.info('fetch_url={}'.format(url))

        with urlopen(url) as in_f:
            b = in_f.read()

        return b

    def fetch_image(self) -> (bytes, str):
        url, name = self.image_url()
        return self._fetch(url), name


class BingSource(POTDSource):

    def image_url(self) -> (str, str):
        base_url = "https://www.bing.com"
        json_url = "/HPImageArchive.aspx?format=js&idx=0&n=1"

        with urlopen(urljoin(base_url, json_url)) as in_f:
            json_obj = json.loads(in_f.read().decode("UTF-8"))

        url = None if json_obj is None else urljoin(base_url, json_obj["images"][0]["url"])
        name = parse_qs(urlparse(url).query)['id'][0]

        return url, name

    @retry(attempts=5, delay=2)
    def fetch_image(self) -> (bytes, str):
        return super().fetch_image()


class NASASource(POTDSource):

    def image_url(self) -> (str, str):
        base_url = "https://apod.nasa.gov/apod"
        pattern = "<a href=\"(image/.*)\""
        url = self._fetch_and_parse(base_url, pattern)
        return url, os.path.basename(url)

    @retry(attempts=5, delay=5)
    def fetch_image(self) -> (bytes, str):
        return super().fetch_image()


class NatGeoSource(POTDSource):

    def image_url(self) -> (str, str):
        base_url = "http://www.nationalgeographic.com/photography/photo-of-the-day/"
        pattern = "<meta\s+property=\"og:image\"\s+content=\"(.*?)\".*/>"
        url = self._fetch_and_parse(base_url, pattern)
        return url, os.path.basename(url)

    @retry(attempts=5, delay=5)
    def fetch_image(self) -> (bytes, str):
        return super().fetch_image()
