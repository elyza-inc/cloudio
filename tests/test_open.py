import pandas as pd
import pytest
from cloudio import cloudio_config, copen


def test_open_read_s3():
    with copen("s3://elyza-datasets/JapaneseSQuAD/source/README.md") as f:
        text = f.read()
    assert text[:16] == "# Japanese SQuAD"


def test_open_read_local():
    with copen("pyproject.toml") as f:
        text = f.read()
    assert text[:13] == "[tool.poetry]"


def test_open_read_fileobj():
    url = "s3://elyza-datasets/JapaneseSQuAD/source/wiki_top_long_paragraphs.json"
    with copen(url) as f:
        df = pd.read_json(f, orient="records", lines=True)
    df.head()


def test_open_write_s3():
    with cloudio_config(s3_profile="elyza"), copen(
        "s3://elyza-datasets/JapaneseSQuAD/hoge.txt", "w"
    ) as f:
        f.write("hogefuga")


def test_open_raise_not_found():
    with pytest.raises(FileNotFoundError):
        with cloudio_config(s3_profile="elyza"), copen(
            "s3://elyza-datasets/fuga.txt", "r"
        ) as f:
            text = f.read()
