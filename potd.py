#!/usr/bin/python3
# Save photo of the day to dropbox
import imghdr
import sys
import time
import uuid
import os
import schedule

from helper import *
from config import *
from retry_deco import retry

import bing_provider
import natgeo_provider
import nasa_apod_provider

providers = [bing_provider, nasa_apod_provider, natgeo_provider]


@retry(tries=10, delay=10)
def do():
    dbx_token = env('DBX_TOKEN', DBX_TOKEN)
    dbx_path = env('DBX_PATH', DBX_PATH)
    gdrive_folder = env('GDRIVE_FOLDER_ID', GDRIVE_FOLDER_ID)
    for provider in providers:
        try:
            url, name = provider.fetch_url()
        except:
            continue

        log.info('fetch_url={}'.format(url))

        with urlopen(url) as in_f:
            b = in_f.read()

        if name is None or name.strip() == "":
            name = "{}.{}".format(uuid.uuid4(), imghdr.what(None, b))

        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)

        write_to_file(TMP_DIR, name, b)

        try:
            if os.path.exists(TMP_DIR):
                for root, dirs, files in os.walk(TMP_DIR):
                    for f in files:
                        basename = os.path.basename(f)
                        with open(os.path.join(root, f), "rb") as _in:
                            b = _in.read()
                        try:
                            #upload_dbx(dbx_token, b, dbx_path + basename)
                            #write_to_file(out_dir, basename, b)
                            upload_gdrive(gdrive_folder, os.path.join(root, f))
                            os.remove(os.path.join(root, f))
                        except Exception as e:
                            log.exception(e)
        except Exception as e:
            log.exception(e)
            log.warning("Retry next time...")


if __name__ == "__main__":
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

    gauth()

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
