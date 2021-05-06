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
