from pathlib import Path
from typing import Union
from urllib.parse import urlparse

from cloudio.s3 import s3_upload_file


def upload(url: str, path: Union[str, Path]):
    parsed = urlparse(url)
    if parsed.scheme == "s3":
        if Path(path).is_dir():
            raise NotImplementedError
        else:
            s3_upload_file(url=url, filename=path)
    else:
        raise NotImplementedError("Uploading except S3 is not implemented.")
