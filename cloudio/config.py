import os
from contextlib import contextmanager
from typing import Any, Dict

__CONFIG = {
    "cache_dir": f"{os.environ.get('HOME')}/.cloudio/cache/",
    "s3_profile": None,
    "upload_tmp_dir": f"{os.environ.get('HOME')}/.cloudio/upload_tmp/",
}


def set_config(**kwargs: Any) -> None:
    for key, val in kwargs.items():
        if key not in __CONFIG.keys():
            raise KeyError(key)
        __CONFIG[key] = val


def get_config(key: str) -> Any:
    return __CONFIG[key]


def get_all_config() -> Dict[str, Any]:
    return __CONFIG.copy()


@contextmanager
def cloudio_config(**kwargs: Any):
    current_config = get_all_config()
    set_config(**kwargs)
    yield
    set_config(**current_config)
