from urllib.parse import urlparse

from cloudio.s3 import s3_remove


def remove(url: str) -> None:
    """指定されたURLのオブジェクトを削除する。

    ディレクトリを指定した場合はそのディレクトリ以下全てを削除する。
    ローカルのファイルにも対応したり、recursive=Falseなどのオプションを実装した方が良いかも
    """
    parsed = urlparse(url)
    if parsed.scheme == "s3":
        s3_remove(url=url)
    else:
        raise NotImplementedError("Removing except S3 is not implemented.")
