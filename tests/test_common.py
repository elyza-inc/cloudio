from pathlib import Path

from cloudio.utils import format_path_or_url


def test_format_path_or_url():
    url = "http://hoge/fuga.txt"
    assert format_path_or_url(Path(url)) == url

    url = "https://hoge/fuga.txt"
    assert format_path_or_url(Path(url)) == url

    url = "s3://hoge/fuga.txt"
    assert format_path_or_url(Path(url)) == url

    url = "https://elyza-sandbox.s3.amazonaws.com/liz_ocr/shadow_sample1.jpg"
    assert format_path_or_url(Path(url)) == url
