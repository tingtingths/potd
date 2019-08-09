import re
import os
import logging
from urllib.parse import urljoin
from urllib.request import urlopen

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from dropbox import dropbox

from config import log


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
        os.makedirs(path)

    with open(os.path.join(path, filename), "wb") as out:
        out.write(bin)

    log.info('write file done, name: ' + filename)

    return os.path.join(path, filename)


def gauth():
    gauth = GoogleAuth()
    # Create local webserver and auto handles authentication.
    gauth.LocalWebserverAuth()

    return gauth


def _gdrive_get_file(drive, folder_id, title):
    file_list = drive.ListFile({'q': "'" + folder_id + "' in parents and trashed=False"}).GetList()
    for f in file_list:
        if f['title'] == title:
            return f

    return None


def upload_gdrive(folder_id, local_file):
    drive = GoogleDrive(gauth())
    name = os.path.basename(local_file)

    gfile = _gdrive_get_file(drive, folder_id, name)
    if gfile is None:
        gfile = drive.CreateFile({
            'title': name,
            'parents': [{'id': folder_id}]
        })
    gfile.SetContentFile(local_file)
    gfile.Upload()
