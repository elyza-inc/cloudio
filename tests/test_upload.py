from cloudio import cloudio_config
from cloudio.upload import upload, upload_later


def test_upload():
    upload("s3://elyza-sandbox/cloudio/README.md", "README.md")


def test_upload_later():
    with upload_later("s3://elyza-sandbox/cloudio/hoge.txt") as local_tmp_file:
        with open(local_tmp_file, "w") as f:
            f.write("hoge")
