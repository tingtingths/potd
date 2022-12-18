#!/usr/bin/env python3
# Save picture of the day
import argparse
import imghdr
import time
import uuid
from datetime import date

import schedule

from config import *
from potd_source import *
from storage import StorageProvider, DropboxProvider, GoogleDriveProvider

sources = [BingSource(), NatGeoSource(), NASASource()]


def _write_to_file(path, filename, b):
    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.path.join(path, filename), "wb") as out:
        out.write(b)

    log.info('write file done, name: ' + filename)

    return os.path.join(path, filename)


def valid_time_str(s):
    try:
        from datetime import datetime
        datetime.strptime(s, "%H:%M")
        return s
    except ValueError:
        raise argparse.ArgumentTypeError(f'Invalid time format {s}')


def download_pictures_from_sources(fs: StorageProvider, base: str, group_by_date: bool = False):
    for source in sources:
        data, name = source.fetch_image()

        if data is None:
            continue

        if name is None or name.strip() == "":
            name = "{}.{}".format(uuid.uuid4(), imghdr.what(None, data))

        download_dir = os.path.join(TMP_DIR, date.strftime(date.today(), '%Y-%m-%d')) if group_by_date else TMP_DIR
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        _write_to_file(download_dir, name, data)

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
    parser.add_argument('--at-time', '-t', type=valid_time_str,
                        help='Time string indicating the time to retrieve images, '
                             'in the following format HH:MM. '
                             'This will also enable the internal scheduler, '
                             'thus making the script runs indefinitely. '
                             'Do not use this if you intend to use external scheduler, e.g. cron')
    parser.add_argument('--dropbox-token', type=str, help='Authentication token for Dropbox')
    parser.add_argument('--group-by-date', action='store_true', help='Download to dated folder')

    args = parser.parse_args()
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

    storage: StorageProvider = None
    if args.storage == 'dropbox':
        storage = DropboxProvider().create(token=args.dropbox_token)
    if args.storage == 'gdrive':
        storage = GoogleDriveProvider().create()
    storage.auth()

    if args.at_time is None:
        download_pictures_from_sources(storage, args.base_dir, group_by_date=args.group_by_date)
    else:
        # start daemon for internal schedule
        log.info('Setup internal scheduler...')
        schedule.every().day.at(args.at_time).do(download_pictures_from_sources, storage, args.base_dir,
                                                 group_by_date=args.group_by_date)
        schedule.run_all()  # run now
        [log.info("JOB - %s", str(job)) for job in schedule.jobs]
        while True:
            schedule.run_pending()
            time.sleep(1)
