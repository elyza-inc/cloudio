import logging
import os
from configparser import ConfigParser
from functools import wraps
from pathlib import Path
from typing import IO, Callable, Optional, Tuple, Union
from urllib.parse import urlparse

import boto
import boto3
import botocore
from botocore.exceptions import ClientError, ProfileNotFound

from cloudio.config import get_config
from tqdm import tqdm

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
    if s3_profile is None:
        # credential_source = get_credential_source()
        # if credential_source is None:
        if not has_default_credentials():
            return boto3.resource(
                "s3", config=botocore.client.Config(signature_version=botocore.UNSIGNED)
            )
        else:
            return boto3.resource("s3")

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


@s3_request
def s3_upload_folder(url: str, path: Union[str, Path]) -> None:
    s3_resource = get_s3_resource()
    bucket_name, s3_path = split_s3_path(url)
    files = sorted([p for p in Path(path).rglob("*") if p.is_file()])
    for file in tqdm(files):
        tgt_url = os.path.join(s3_path, str(file.relative_to(path)))
        s3_resource.Bucket(bucket_name).upload_file(Filename=str(file), Key=tgt_url)


@s3_request
def s3_remove(url: str) -> None:
    s3_resource = get_s3_resource()
    bucket_name, s3_path = split_s3_path(url)
    s3_resource.Bucket(bucket_name).objects.filter(Prefix=s3_path).delete()


def get_credential_source() -> Optional[str]:
    """AWSのcredential_sourceを返す。設定されていない場合はNoneとなる"""
    aws_config_file = os.environ.get(
        "AWS_CONFIG_FILE", str(Path.home() / ".aws/config")
    )

    if not Path(aws_config_file).exists():
        return None

    aws_config = ConfigParser()
    aws_config.read(aws_config_file)

    try:
        credential_source = aws_config["default"]["credential_source"]
    except KeyError:
        return None
    else:
        return credential_source


def has_default_credentials() -> bool:
    """環境変数やコンフィグファイルなど、プログラムへの入力以外の方法で設定された認証情報があるかどうかを返す

    !!! note
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#configuring-credentials
    ```
    boto3の資格情報検索メカニズムは、以下のリストに沿って検索し、資格情報を見つけたらそこで停止することです。Boto3が資格情報を検索する順序は:

    boto.client() メソッドにパラメーターで渡された資格情報
    Session オブジェクトの生成時にパラメーターで渡された資格情報
    環境変数
    共有された認証情報ファイル（~/.aws/credentials）
    AWS設定ファイル（~/.aws/config）
    ロールの引き受けの提供
    Boto2設定ファイル（/etc/boto.cfg and ~/.boto）
    IAMロールを構成されたAmazon EC2インスタンス上ではそのインスタンスメタデータサービス
    ```
    """
    # 1. 環境変数
    if os.environ.get("AWS_ACCESS_KEY_ID") is not None:
        return True

    # 2. 共有された認証情報ファイル（~/.aws/credentials）
    aws_credentials_file = os.environ.get(
        "AWS_SHARED_CREDENTIALS_FILE", str(Path.home() / ".aws/credentials")
    )
    if Path(aws_credentials_file).exists():
        aws_credentials = ConfigParser()
        aws_credentials.read(aws_credentials_file)
        try:
            _ = aws_credentials["default"]["aws_access_key_id"]
        except KeyError:
            pass
        else:
            return True

    # 3. AWS設定ファイル（~/.aws/config）
    # 以下の理由により、これのチェックは行わない
    # 通常は、AWS設定ファイル内で管理しているプロファイル情報はリージョン（region）とデフォルトの出力形式（output）で、認証情報は含まれていません

    # TODO: ロールの引き受けの提供

    # 4. Boto2設定ファイル（/etc/boto.cfg and ~/.boto）
    aws_access_key_id = boto.config.get_value("Credentials", "aws_access_key_id")
    if aws_access_key_id is not None:
        return True

    # 5. IAMロールを構成されたAmazon EC2インスタンス上ではそのインスタンスメタデータサービス
    credential_source = get_credential_source()
    if credential_source is not None:
        return True

    return False
