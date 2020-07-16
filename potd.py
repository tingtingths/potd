#!/usr/bin/python3
# Save picture of the day
import argparse
import imghdr
import time
import uuid

import schedule

from config import *
from potd_source import *
from retry_deco import retry
from storage import StorageProvider, DropboxProvider, GoogleDriveProvider

sources = [BingSource(), NatGeoSource(), NASASource()]


def _write_to_file(path, filename, b):
    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.path.join(path, filename), "wb") as out:
        out.write(b)

    log.info('write file done, name: ' + filename)

    return os.path.join(path, filename)


@retry(attempts=10, delay=10)
def do(fs: StorageProvider, base: str):
    for source in sources:
        data, name = source.fetch_image()

        if name is None or name.strip() == "":
            name = "{}.{}".format(uuid.uuid4(), imghdr.what(None, data))

        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)

        _write_to_file(TMP_DIR, name, data)

    # upload everything from the tmp directory
    try:
        if os.path.exists(TMP_DIR):
            for root, dirs, files in os.walk(TMP_DIR):
                for f in files:
                    filename = os.path.basename(f)
                    with open(os.path.join(root, f), "rb") as _in:
                        b = _in.read()
                    try:
                        fs.put(base, filename, b)
                        os.remove(os.path.join(root, f))
                    except Exception as e:
                        log.exception(e)
    except Exception as e:
        log.exception(e)
        log.warning("Retry next time...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Picture of the day.')
    parser.add_argument('--storage', choices=['dropbox', 'gdrive', 'local'],
                        help='Storage provider', required=True)
    parser.add_argument('--base-dir', type=str,
                        help='Place to keep the images. If you\'re using Google Drive, this would be the folder ID. '
                             'Otherwise, the folder path.', required=True)
    parser.add_argument('--interval', '-i', type=int,
                        help='Interval in hours to retrieve images. This will also enable the internal scheduler, '
                             'thus making the script runs indefinitely. '
                             'Do not use this if you intend to use external scheduler, e.g. cron')
    parser.add_argument('--dropbox-token', type=str, help='Authentication token for Dropbox')

    args = parser.parse_args()
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

    storage: StorageProvider = None
    if args.storage == 'dropbox':
        storage = DropboxProvider().create(token=args.dropbox_token)
    if args.storage == 'gdrive':
        storage = GoogleDriveProvider().create()
    storage.auth()

    if args.interval is None:
        do(storage, args.base_dir)
    else:
        # start daemon for internal schedule
        log.info('Setup internal scheduler...')
        schedule.every(args.interval).hours.do(do, storage, args.base_dir)
        [log.info("JOB - %s", str(job)) for job in schedule.jobs]
        while True:
            schedule.run_pending()
            time.sleep(1)
