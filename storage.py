import os
import tempfile
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
        return self

    @abstractmethod
    def auth(self):
        pass

    @abstractmethod
    def get(self, base: str, filename: str):
        pass

    @abstractmethod
    def put(self, base: str, filename: str, data: bytes):
        pass


class LocalFSProvider(StorageProvider):

    def auth(self):
        pass

    def get(self, base: str, filename: str):
        with open(os.path.join(base, filename), 'rb') as f:
            b = f.read()
        return b

    def put(self, base: str, filename: str, data: bytes):
        with open(os.path.join(base, filename), 'wb') as f:
            f.write(data)


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

    def auth(self, oauth=False):
        gauth = GoogleAuth()
        if oauth:
            gauth.LocalWebserverAuth()
        else:
            gauth.CommandLineAuth()
        self.drive = GoogleDrive(gauth)

    def get(self, base: str, filename: str):
        if self.drive is None:
            raise RuntimeError('No authorized Google Drive instance found.')

        found = self.drive.ListFile({
            'q': f'\'{base}\' in parents and title=\'{filename}\' and trashed=False'
        }).GetList()

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

        fd, name = tempfile.mkstemp()
        try:
            with open(name, 'wb') as tmp:
                tmp.write(data)
            os.close(fd)

            gfile.SetContentFile(name)
            gfile.Upload()
            log.info(f'[{type(self).__name__}] Uploaded. name={filename}')
        finally:
            os.close(fd)
            os.remove(name)
