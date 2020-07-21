from pathlib import Path

from cloudio.utils import to_str


def test_to_str():
    url = "http://hoge/fuga.txt"
    assert to_str(Path(url)) == url

    url = "https://hoge/fuga.txt"
    assert to_str(Path(url)) == url

    url = "s3://hoge/fuga.txt"
    assert to_str(Path(url)) == url

    url = "https://elyza-sandbox.s3.amazonaws.com/liz_ocr/shadow_sample1.jpg"
    assert to_str(Path(url)) == url
