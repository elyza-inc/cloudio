from cloudio.s3 import get_credential_source, has_default_credentials


def test_get_credential_source():
    cs = get_credential_source()
    assert cs is None


def test_has_default_credentials():
    assert not has_default_credentials()
