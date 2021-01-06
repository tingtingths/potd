# potd
Save photo of the day to cloud storage.

Sources
  - Bing
  - NASA
  - National Geographic

Storages
  - Google Drive
  - Dropbox
  - local

## Usage
```sh
usage: potd.py [-h] --storage {dropbox,gdrive,local} --base-dir BASE_DIR [--at-time AT_TIME]
               [--dropbox-token DROPBOX_TOKEN]

Picture of the day.

optional arguments:
  -h, --help            show this help message and exit
  --storage {dropbox,gdrive,local}
                        Storage provider
  --base-dir BASE_DIR   Place to keep the images. If you're using Google Drive, this would be the folder ID.
                        Otherwise, the folder path.
  --at-time AT_TIME, -t AT_TIME
                        Time string indicating the time to retrieve images, in the following format HH:MM. This will
                        also enable the internal scheduler, thus making the script runs indefinitely. Do not use this
                        if you intend to use external scheduler, e.g. cron
  --dropbox-token DROPBOX_TOKEN
                        Authentication token for Dropbox
```
