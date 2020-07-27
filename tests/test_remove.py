from cloudio.remove import remove
from cloudio.upload import upload_folder


def test_remove():
    upload_folder("s3://elyza-sandbox/cloudio/remove_test", "tests/")
    remove("s3://elyza-sandbox/cloudio/remove_test")
