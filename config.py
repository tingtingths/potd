DBX_TOKEN = "<dropbox token>"
DBX_PATH = "<dropbox path for upload>"


def env_token():
    import os
    if 'DBX_TOKEN' not in os.environ:
        return None
    return os.environ['DBX_TOKEN']


def env_path():
    import os
    if 'DBX_PATH' not in os.environ:
        return None
    return os.environ['DBX_PATH']