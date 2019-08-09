import re
import os
from config import *
import dropbox
from urllib.parse import urljoin
from urllib.request import urlopen


def fetch_and_parse(base_url, pattern):
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


def upload_dbx(token, data, path):
    dbx = dropbox.Dropbox(token)
    result = dbx.files_upload(data, path)
    log.info("upload done, name: " + result.name)


def write_to_file(path, filename, bin):
    if not os.path.exists(path):
        os.makedirs(pathq)

    with open(os.path.join(path, filename), "wb") as out:
        out.write(bin)

    return os.path.join(path, filename)
