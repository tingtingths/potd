import logging
import bing_provider
import nasa_apod_provider
import natgeo_provider


DBX_TOKEN = "<dropbox token>"
DBX_PATH = "<dropbox path for upload>"


formatter = logging.Formatter('[%(levelname)s] %(asctime)s | %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logging.getLogger('').addHandler(sh)
logging.getLogger('').setLevel(logging.INFO)

TMP_DIR = ".pending"
OUT_DIR = "/potd_out"

providers = [bing_provider, nasa_apod_provider, natgeo_provider]
log = logging.getLogger("")


def env(key, default=None):
    import os
    if key not in os.environ:
        return default
    return os.environ[key]
