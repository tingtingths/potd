import logging
import os

DBX_TOKEN = "<dropbox token>"
DBX_PATH = "<dropbox path for upload>"

GDRIVE_FOLDER_ID = "<folder_id>"

formatter = logging.Formatter('[%(levelname)s] %(asctime)s | %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logging.getLogger('').addHandler(sh)
logging.getLogger('').setLevel(logging.INFO)

TMP_DIR = ".pending"

log = logging.getLogger("")


def env(key, default=None):
    if key not in os.environ:
        return default
    return os.environ[key]
