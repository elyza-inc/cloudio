import pandas as pd

from cloudio import copen

# import cloudio
# cloudio.set_config(s3_profile="elyza")


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
    with copen("s3://elyza-datasets/JapaneseSQuAD/hoge.txt", "w") as f:
        f.write("hogefuga")
