import os
import uuid
from abc import ABC, abstractmethod
from urllib.parse import urljoin

from dropbox import dropbox
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from config import log


class StorageProvider(ABC):
    _args = {}

    def create(self, **kwargs):
        self._args = kwargs

    @abstractmethod
    def auth(self):
        pass

    @abstractmethod
    def get(self, base: str, filename: str):
        pass

    @abstractmethod
    def put(self, base: str, filename: str, data: bytes):
        pass


class DropboxProvider(StorageProvider):
    dbx = None

    def auth(self):
        self.dbx = dropbox.Dropbox(self._args['token'])

    def get(self, base: str, filename: str):
        if self.dbx is None:
            raise RuntimeError('No authorized Dropbox instance found.')

        path = urljoin(base, filename)
        return self.dbx.files_download(path)

    def put(self, base: str, filename: str, data: bytes):
        if self.dbx is None:
            raise RuntimeError('No authorized Dropbox instance found.')

        path = urljoin(base, filename)
        result = self.dbx.files_upload(data, path)
        log.info(f'[{type(self).__name__}] Uploaded. name={result.name}')


class GoogleDriveProvider(StorageProvider):
    drive = None

    def auth(self):
        gauth = GoogleAuth()
        gauth.CommandLineAuth()
        self.drive = GoogleDrive(gauth)

    def get(self, base: str, filename: str):
        if self.drive is None:
            raise RuntimeError('No authorized Google Drive instance found.')

        files = self.drive.ListFile({
            'q': f'\'{base}\' in parents and trashed=False'
        }).GetList()
        found = list(filter(lambda f: f['title'] == filename, files))

        if len(found) > 0:
            return found[0]
        return None

    def put(self, base: str, filename: str, data: bytes):
        if self.drive is None:
            raise RuntimeError('No authorized Google Drive instance found.')

        gfile = self.get(base, filename)
        if gfile is None:
            gfile = self.drive.CreateFile({
                'title': filename,
                'parents': [{'id': base}]
            })

        tmp_file_name = uuid.uuid4().hex
        with open(tmp_file_name, 'rb') as tmp_file:
            tmp_file.write(data)
        gfile.SetContentFile(tmp_file_name)
        gfile.Upload()
        os.remove(tmp_file_name)
