"""Sync s3 files to local motoserver using s3-read-only credentials."""

import sys

import boto3
from botocore.client import BaseClient as AWSClient

from auth import get_read_only_s3_client
from cache import object_cache
from vars import (
    MOTO_ACCESS_KEY,
    MOTO_ACCESS_SECRET_KEY,
    MOTO_SERVER_ENDPOINT,
)


def list_bucket_objects(client: AWSClient, bucket: str, prefix: str = "") -> list:
    """List all objects in a bucket with optional prefix."""
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for item in page.get("Contents", []):
            yield item["Key"], item["ETag"].strip('"')


def motoserver_s3_client() -> AWSClient:
    """Return S3 client with write access to motoserver bucket."""
    return boto3.client(
        "s3",
        aws_access_key_id=MOTO_ACCESS_KEY,
        aws_secret_access_key=MOTO_ACCESS_SECRET_KEY,
        endpoint_url=MOTO_SERVER_ENDPOINT,
    )


def sync(bucket: str, prefix: str) -> None:
    """Synchronize a real S3 bucket with the local motoserver."""
    # Source bucket; This connects to a real S3 bucket!!
    source = get_read_only_s3_client()

    # Destination bucket; This connects to a fake S3 bucket.
    destination = motoserver_s3_client()

    # Get the current state of the source and destination buckets.
    source_objects = list_bucket_objects(source, bucket, prefix=prefix)
    destination_objects = list_bucket_objects(destination, bucket, prefix=prefix)

    # Find unsynchronized files using Key and ETag combinations to compare.
    print("Comparing bucket states...")
    unsynced = set(source_objects) - set(destination_objects)

    print(f"{len(unsynced)} unsynchronized files found.")

    if not unsynced:
        print("\nNothing to do.")
        return

    # Copy all objects which were not found in the motoserver S3 bucket.
    print("Beginning synchronization:")
    for object_key, etag in unsynced:
        body = object_cache(source, bucket, object_key, etag)

        tag_data = source.get_object_tagging(Bucket=bucket, Key=object_key)
        print("🢂 Syncing to Motoserver")
        destination.put_object(
            Bucket=bucket,
            Key=object_key,
            Body=body,
        )
        if tag_data["TagSet"]:
            print(f"🢂 Syncing tags to Motoserver: {tag_data['TagSet']}")
            destination.put_object_tagging(
                Bucket=bucket,
                Key=object_key,
                Tagging={"TagSet": tag_data["TagSet"]},
            )

    print("\nSynchronization complete.")


if __name__ == "__main__":
    try:
        bucket = sys.argv[1]
        prefix = sys.argv[2]
    except IndexError:
        bucket = ""
        prefix = ""

    if not bucket or not prefix:
        print("Usage: moto_sync_from_s3.py <bucket> <prefix>")
        exit(1)
    print(f"Syncing motoserver bucket {bucket} with prefix {prefix}...")
    sync(bucket, prefix)
    exit(0)
