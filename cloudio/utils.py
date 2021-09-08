import re
from pathlib import Path
from typing import Union


def fix_drive_str_in_path(path: str) -> str:
    fixed = re.sub(r':/(?!/)', '://', path)
    return fixed


def format_path_or_url(path_or_url: Union[str, Path]) -> str:
    """ローカルへのパスまたはURLをstr型に変換する

    単純にs3のパスをPath('s3://hoge')などとしてしまうと、//が/に変換され Path('s3:/hoge/fuga')
    として保持されてしまうことヘの暫定的な対処
    """
    if isinstance(path_or_url, str):
        return path_or_url
    elif isinstance(path_or_url, Path):
        path_or_url_str = str(path_or_url)
        path_or_url_str = fix_drive_str_in_path(path_or_url_str)
        return path_or_url_str
    else:
        raise TypeError


def format_path_with_drive(path: Path) -> str:
    """Formats `pathlib.Path` object."""

    # below is the copy-and-paste of `pathlib.Path.__str__`
    try:
        formatted = path._str
    except AttributeError:
        formatted = path._format_parsed_parts(path._drv, path._root, path._parts) or '.'

    formatted = fix_drive_str_in_path(formatted)
    return formatted


def override_pathlib_str_for_drive() -> None:
    """Replaces `Path.__str__` with `format_path_with_drive`"""
    Path.__str__ = format_path_with_drive


def override_pathlib_open_with_copen() -> None:
    """
    Replaces `pathlib.Path.open` with `cloudio.copen`. This function imitates
    `smart_open.smart_open_lib.patch_pathlib`.
    """
    def _open(path_or_uri: Union[str, Path], mode: str = 'r', **kwargs):
        path_or_uri = format_path_or_url(path_or_uri)
        f = cloudio.copen(path_or_uri, mode=mode, **kwargs)
        return f

    Path.open = _open
