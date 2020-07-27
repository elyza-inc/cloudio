from pathlib import Path

from cloudio.upload import upload, upload_folder, upload_later


def test_upload_00():
    upload("s3://elyza-sandbox/cloudio/README.md", "README.md")


def test_upload_01():
    upload(Path("s3://elyza-sandbox/cloudio/README.md"), "README.md")


def test_upload_later():
    with upload_later("s3://elyza-sandbox/cloudio/hoge.txt") as local_tmp_file:
        with open(local_tmp_file, "w") as f:
            f.write("hoge")


def test_upload_folder():
    upload_folder("s3://elyza-sandbox/cloudio/upload_folder", "tests/")
