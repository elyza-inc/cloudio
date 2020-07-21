import os
from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import Union
from urllib.parse import urlparse
from uuid import uuid4

from cloudio import get_config
from cloudio.s3 import s3_upload_file

logger = getLogger(__name__)


def upload(url: str, path: Union[str, Path]):
    parsed = urlparse(url)
    if parsed.scheme == "s3":
        if Path(path).is_dir():
            raise NotImplementedError
        else:
            s3_upload_file(url=url, filename=path)
    else:
        raise NotImplementedError("Uploading except S3 is not implemented.")


@contextmanager
def upload_later(cloud_or_local_path: Union[str, Path]):
    parsed = urlparse(cloud_or_local_path)

    # If path is local path, then yield it
    if Path(cloud_or_local_path).parent.exists():
        yield cloud_or_local_path

    # Upload to some cloud storage
    elif parsed.scheme in ("s3", "gs"):

        # Write to temp file
        temp_path = (
            Path(get_config("upload_tmp_dir"))
            / str(uuid4())
            / Path(cloud_or_local_path).name
        )
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        yield temp_path

        # if succeeded to write tempfile, then upload temp file to cloud
        try:
            upload(cloud_or_local_path, temp_path)
        except Exception:
            logger.error(
                f"Upload to {cloud_or_local_path} failed. You can accesss {temp_path}"
            )
            raise
        else:
            logger.info(
                f"Upload to {cloud_or_local_path} succeeded. Deleting temp file..."
            )
            os.remove(str(temp_path))

    else:
        raise ValueError(f"Given url_or_path {cloud_or_local_path} is invalid.")
