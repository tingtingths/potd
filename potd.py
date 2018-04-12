#!/usr/bin/python3
# Save photo of the day to dropbox
import imghdr
import logging
import os
import sys
import time
import uuid
from urllib.request import urlopen

import dropbox
import schedule

import bing_provider
import nasa_apod_provider
import natgeo_provider
from config import *
from retry_deco import retry

formatter = logging.Formatter('[%(levelname)s] %(asctime)s | %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logging.getLogger('').addHandler(sh)
logging.getLogger('').setLevel(logging.INFO)

TMP_DIR = "~/pending_bing_upload"

providers = [bing_provider, nasa_apod_provider, natgeo_provider]
log = logging.getLogger("")


def upload_dbx(token, data, path):
    dbx = dropbox.Dropbox(token)
    result = dbx.files_upload(data, path)
    log.info("upload done, name: " + result.name)


@retry(tries=10, delay=10)
def do():
    dbx_token = DBX_TOKEN if env_token() is None else env_token()
    dbx_path = DBX_PATH if env_path() is None else env_path()
    for provider in providers:
        url = provider.fetch_url()
        name = os.path.basename(url)

        log.info('fetch_url={}'.format(url))

        with urlopen(url) as in_f:
            b = in_f.read()

        if name is None or name.strip() == "":
            name = "{}.{}".format(uuid.uuid4(), imghdr.what(None, b))

        try:
            upload_dbx(dbx_token, b, os.path.join(dbx_path, name))
            if os.path.exists(TMP_DIR):
                for root, dirs, files in os.walk(TMP_DIR):
                    for f in files:
                        basename = os.path.basename(f)
                        with open(os.path.join(root, f), "rb") as _in:
                            b = _in.read()
                        try:
                            upload_dbx(dbx_token, b, dbx_path + basename)
                            os.remove(os.path.join(root, f))
                        except Exception as e:
                            log.exception(e)
        except Exception as e:
            log.exception(e)
            # save to local and try again next time
            log.warning("Wait for retry next time...")
            if not os.path.exists(TMP_DIR):
                os.makedirs(TMP_DIR)
            with open(os.path.join(TMP_DIR, name), "wb") as out:
                out.write(b)
            log.warning("Saved")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'schedule':
        # start daemon for internal schedule
        log.info('Setup internal scheduler...')
        schedule.every().day.at('20:00').do(do)
        [log.info("JOB - %s", str(job)) for job in schedule.jobs]
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        do()
