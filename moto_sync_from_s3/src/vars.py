"""Constants for the extension and modules."""

import os
from pathlib import Path

# AWS Environment Variabls
AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]
AWS_CLIENT_SESSION_NAME = os.getenv("AWS_CLIENT_SESSION_NAME", "tilt-moto_sync_from_s3")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_ROLE_NAME = os.environ["AWS_S3_ROLE_NAME"]
AWS_SSO_WEB_START_URL = os.environ["AWS_SSO_WEB_START_URL"]

# Motoserver Defaults
MOTO_SERVER_ENDPOINT = os.getenv("MOTO_SERVER_ENDPOINT", "http://motoserver:3000")
MOTO_ACCESS_KEY = os.getenv("MOTO_ACCESS_KEY", "A")
MOTO_ACCESS_SECRET_KEY = os.getenv("MOTO_ACCESS_SECRET_KEY", "B")

# Path to cache root
EXTENSION_PATH_PATH = Path(__file__).parents[1]
CACHE_PATH = EXTENSION_PATH_PATH / ".cache"

# Object cache subdirectory
S3_OBJECT_CACHE = CACHE_PATH / "objects"
S3_OBJECT_CACHE.mkdir(parents=True, exist_ok=True)

# Credential cache subdirectory
CACHED_CREDENTIALS_PATH = CACHE_PATH / "credentials"
CACHED_CREDENTIALS_PATH.mkdir(parents=True, exist_ok=True)
