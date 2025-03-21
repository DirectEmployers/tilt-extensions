from botocore.client import BaseClient as AWSClient

from vars import S3_OBJECT_CACHE


def object_cache(source: AWSClient, bucket: str, object_key: str, etag: str) -> bytes:
    """Check for object in local disk cache first, get from S3 on cache miss."""
    partitioned_path = make_partitioned_path(etag, size=4)
    object_path = partitioned_path / etag
    if object_path.exists():
        print(f"🡾 Loading from cache: {bucket}:{object_key} ", end="")
        body = object_path.read_bytes()
    else:
        print(f"🡾 Downloading from S3: {bucket}:{object_key} ", end="")
        s3_object = source.get_object(Bucket=bucket, Key=object_key)
        body = s3_object["Body"].read()
        # Cache object by etag
        print(f"\n🡾 Caching object {object_key} with etag as key: {etag}")
        object_path.write_bytes(body)

    return body


def make_partitioned_path(etag: str, size: int):
    """Return a partitioned path for a given etag, to avoid limits of inodes, etc.

    Etags are hexadecimal, so we can split it up to ensure we don't exceed limits.

    Max files per path based on `size`:
    - 3 (FFF) == 4,095 files per path
    - 4 (FFFF) == 65,535 files per path
    - 5 (FFFFF) == 1,048,575 files per path
    """
    partitioned = [etag[i : i + size] for i in range(0, len(etag), size)]
    partitioned_path = S3_OBJECT_CACHE.joinpath(*partitioned)
    partitioned_path.mkdir(parents=True, exist_ok=True)

    return partitioned_path
