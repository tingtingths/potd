#!/usr/bin/python3
# Save photo of the day to dropbox
import os
from urllib.request import urlopen

import dropbox

import bing_provider
import nasa_apod_provider
import natgeo_provider

from config import *
from retry_deco import retry

TMP_DIR = "~/pending_bing_upload"

providers = [bing_provider, nasa_apod_provider, natgeo_provider]


def upload_dbx(token, data, path):
    dbx = dropbox.Dropbox(token)
    result = dbx.files_upload(data, path)
    print("upload done, name: " + result.name)


@retry(tries=10, delay=10)
def do():
    for provider in providers:
        url = provider.fetch_url()
        name = os.path.basename(url)
        with urlopen(url) as in_f:
            b = in_f.read()

        try:
            upload_dbx(DBX_TOKEN, b, os.path.join(DBX_PATH, name))
            if os.path.exists(TMP_DIR):
                for root, dirs, files in os.walk(TMP_DIR):
                    for f in files:
                        basename = os.path.basename(f)
                        with open(os.path.join(root, f), "rb") as _in:
                            b = _in.read()
                        try:
                            upload_dbx(DBX_TOKEN, b, DBX_PATH + basename)
                            os.remove(os.path.join(root, f))
                        except Exception as e:
                            print(e)
        except Exception as e:
            print(e)
            # save to local and try again next time
            print("Wait for retry next time...")
            if not os.path.exists(TMP_DIR):
                os.makedirs(TMP_DIR)
            with open(os.path.join(TMP_DIR, name), "wb") as out:
                out.write(b)
            print("Saved")


if __name__ == "__main__":
    do()
