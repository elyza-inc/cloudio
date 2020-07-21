from cloudio import cached_path, cloudio_config, get_config


def test_cloudio_config(tmpdir):
    with cloudio_config(cache_dir=tmpdir, s3_profile="elyza"):
        path = cached_path("s3://elyza-sandbox/cloudio/README.md")
    assert str(tmpdir) in path
    assert get_config("cache_dir") != str(tmpdir)
