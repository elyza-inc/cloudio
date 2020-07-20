import logging
from functools import wraps
from pathlib import Path
from typing import IO, Callable, Optional, Tuple, Union
from urllib.parse import urlparse

import boto3
import botocore
from botocore.exceptions import ClientError, ProfileNotFound

from cloudio.config import get_config

logger = logging.getLogger(__name__)


def split_s3_path(url: str) -> Tuple[str, str]:
    """Split a full s3 path into the bucket name and path."""
    parsed = urlparse(url)
    if not parsed.netloc or not parsed.path:
        raise ValueError("bad s3 path {}".format(url))
    bucket_name = parsed.netloc
    s3_path = parsed.path
    # Remove '/' at beginning of path.
    if s3_path.startswith("/"):
        s3_path = s3_path[1:]
    return bucket_name, s3_path


def s3_request(func: Callable):
    """
    Wrapper function for s3 requests in order to create more helpful error
    messages.
    """

    @wraps(func)
    def wrapper(url: str, *args, **kwargs):
        try:
            return func(url, *args, **kwargs)
        except ClientError as exc:
            if int(exc.response["Error"]["Code"]) == 404:
                raise FileNotFoundError("file {} not found".format(url))
            else:
                raise

    return wrapper


def get_s3_resource():
    s3_profile = get_config("s3_profile")
    try:
        session = boto3.session.Session(profile_name=s3_profile)
    except ProfileNotFound:
        logger.error(
            "awscliの設定が正しくなされていません。管理者にアクセストークンを発行してもらったのち、"
            f"aws configure --profile {s3_profile} でprofileを登録してください\n"
            "https://qiita.com/itooww/items/bdc2dc15213da43a10a7"
        )
        raise ProfileNotFound(profile=s3_profile)
    if session.get_credentials() is None:
        # Use unsigned requests.
        s3_resource = session.resource(
            "s3", config=botocore.client.Config(signature_version=botocore.UNSIGNED)
        )
    else:
        s3_resource = session.resource("s3")
    return s3_resource


@s3_request
def s3_etag(url: str) -> Optional[str]:
    """Check ETag on S3 object."""
    s3_resource = get_s3_resource()
    bucket_name, s3_path = split_s3_path(url)
    s3_object = s3_resource.Object(bucket_name, s3_path)
    return s3_object.e_tag


@s3_request
def s3_download_file(url: str, filename: Union[str, Path]) -> None:
    s3_resource = get_s3_resource()
    bucket_name, s3_path = split_s3_path(url)
    s3_resource.Bucket(bucket_name).download_fileobj(
        Key=s3_path, Filename=str(filename)
    )


@s3_request
def s3_download_fileobj(url: str, fileobj: IO) -> None:
    s3_resource = get_s3_resource()
    bucket_name, s3_path = split_s3_path(url)
    s3_resource.Bucket(bucket_name).download_fileobj(Key=s3_path, Fileobj=fileobj)


@s3_request
def s3_upload_file(url: str, filename: Union[str, Path]) -> None:
    s3_resource = get_s3_resource()
    bucket_name, s3_path = split_s3_path(url)
    s3_resource.Bucket(bucket_name).upload_file(Filename=str(filename), Key=s3_path)


@s3_request
def s3_upload_fileobj(url: str, fileobj: IO) -> None:
    s3_resource = get_s3_resource()
    bucket_name, s3_path = split_s3_path(url)
    s3_resource.Bucket(bucket_name).upload_fileobj(Fileobj=fileobj, Key=s3_path)