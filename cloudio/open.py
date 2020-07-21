from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import IO, Generator, Union

from cloudio.cached_path import cached_path
from cloudio.upload import upload_later

logger = getLogger(__name__)


@contextmanager
def copen(
    file: Union[str, Path], mode: str = "r", encoding: str = "utf-8", **kwargs
) -> Generator[IO, None, None]:
    f = None
    if "r" in mode:
        try:
            logger.debug(f"Open {file} with kwargs: {kwargs}")
            cache_path = cached_path(file)
            f = open(cache_path, mode=mode, encoding=encoding, **kwargs)
            yield f
        except Exception:
            raise
        finally:
            if f is not None:
                f.close()
            logger.debug(f"Close {file}")

    elif "w" in mode:
        with upload_later(file) as local_tmp_file:
            try:
                f = open(local_tmp_file, mode=mode, encoding=encoding, **kwargs)
                yield f
            except Exception:
                raise
            finally:
                if f is not None:
                    f.close()
                logger.debug(f"Close {file}")
    else:
        raise ValueError(f"mode {mode} is invalid.")
