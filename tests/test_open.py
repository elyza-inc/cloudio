from pathlib import Path

import pandas as pd
import pytest
from cloudio import copen


def test_open_read_s3_00():
    with copen("s3://elyza-sandbox/cloudio/README.md") as f:
        text = f.read()
    assert text[:9] == "# cloudio"


def test_open_read_s3_01():
    with copen(Path("s3://elyza-sandbox/cloudio/README.md")) as f:
        text = f.read()
    assert text[:9] == "# cloudio"


def test_open_read_local():
    with copen("pyproject.toml") as f:
        text = f.read()
    assert text[:13] == "[tool.poetry]"


def test_open_read_fileobj():
    url = "s3://elyza-sandbox/cloudio/fuga.csv"
    with copen(url) as f:
        df = pd.read_csv(f)
    assert df["a"][0] == 1


def test_open_write_s3():
    with copen("s3://elyza-sandbox/cloudio/bar.txt", "w") as f:
        f.write("bar")


def test_open_raise_not_found():
    with pytest.raises(FileNotFoundError):
        with copen("s3://elyza-datasets/not_existing.txt", "r") as f:
            text = f.read()
