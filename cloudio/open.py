import os
from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from urllib.parse import urlparse

from cloudio.cached_path import cached_path
from cloudio.config import get_config
from cloudio.upload import upload

logger = getLogger(__name__)


@contextmanager
def copen(file, mode: str = "r", encoding: str = "utf-8", **kwargs):
    if "r" in mode:
        try:
            logger.debug(f"Open {file} with kwargs: {kwargs}")
            cache_path = cached_path(file)
            f = open(cache_path, mode=mode, encoding=encoding, **kwargs)
            yield f
        except Exception:
            raise
        finally:
            f.close()
            logger.debug(f"Close {file}")

    elif "w" in mode or "x" in mode or "a" in mode:
        parsed = urlparse(file)

        # Write to local file
        if Path(file).parent.exists():
            try:
                f = open(file, mode=mode, encoding=encoding, **kwargs)
            except Exception:
                raise
            else:
                f.close()
            finally:
                return

        # Upload to some cloud storage
        elif parsed.scheme in ("s3", "gs"):
            if "x" in mode or "a" in mode:
                raise NotImplementedError(
                    "Upload to cloud storage with mode x or a is not implemented."
                )

            # Write to temp file
            temp_path = Path(get_config("upload_tmp_dir")) / Path(file).name
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with temp_path.open(mode=mode, encoding=encoding, **kwargs) as temp:
                try:
                    yield temp
                except Exception:
                    raise
                finally:
                    temp.close()

            # if succeeded to write tempfile, then upload temp file to cloud
            try:
                upload(file, temp_path)
            except Exception:
                logger.error(f"Upload to {file} failed. You can accesss {temp_path}")
                raise
            else:
                logger.info(f"Upload to {file} succeeded. Deleting temp file...")
                os.remove(str(temp_path))

        else:
            raise ValueError(f"Given url_or_path {file} is invalid.")
    else:
        raise ValueError(f"mode {mode} is invalid.")
