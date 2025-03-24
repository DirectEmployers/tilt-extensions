import json
import webbrowser
from time import sleep, time

import boto3
from botocore.client import BaseClient as AWSClient

from vars import (
    AWS_ACCOUNT_ID,
    AWS_CLIENT_SESSION_NAME,
    AWS_REGION,
    AWS_S3_ROLE_NAME,
    AWS_SSO_WEB_START_URL,
    CACHED_CREDENTIALS_PATH,
)


CREDENTIALS_PATH = (
    CACHED_CREDENTIALS_PATH / f"{AWS_ACCOUNT_ID}-{AWS_REGION}-{AWS_S3_ROLE_NAME}"
)


def get_credentials() -> dict:
    """Get role credentials and cache them."""
    role_creds = authenticate_with_sso()
    with CREDENTIALS_PATH.open("w") as cc:
        json.dump(role_creds, cc, indent=2)
    return role_creds


def get_read_only_session() -> boto3.session.Session:
    """Get session with read-only access."""
    print(f"Authorizing {AWS_ACCOUNT_ID}::{AWS_S3_ROLE_NAME}")

    if CREDENTIALS_PATH.exists():
        with CREDENTIALS_PATH.open() as cc:
            role_creds = json.load(cc)

        # Expiration is in epoch milliseconds.
        if int(role_creds["expiration"]) < round(time() * 1000):
            # Expired, get fresh credentials.
            role_creds = get_credentials()
    else:
        role_creds = get_credentials()

    return boto3.session.Session(
        aws_access_key_id=role_creds["accessKeyId"],
        aws_secret_access_key=role_creds["secretAccessKey"],
        aws_session_token=role_creds["sessionToken"],
        region_name=AWS_REGION,
    )


def authenticate_with_sso() -> dict:
    """Authenticate with SSO in browser and return role credentials."""
    sso = boto3.client("sso", region_name=AWS_REGION)
    sso_oidc = boto3.client("sso-oidc", region_name=AWS_REGION)

    client_creds = sso_oidc.register_client(
        clientName=AWS_CLIENT_SESSION_NAME,
        clientType="public",
    )
    device_authorization = sso_oidc.start_device_authorization(
        clientId=client_creds["clientId"],
        clientSecret=client_creds["clientSecret"],
        startUrl=AWS_SSO_WEB_START_URL,
    )

    # Launch browser to complete verify client authorization.
    print(f"Authorization Code: {device_authorization['userCode']}")
    webbrowser.open(device_authorization["verificationUriComplete"], autoraise=True)

    token = None
    expires_in = device_authorization["expiresIn"]
    interval = device_authorization["interval"]
    for n in range(1, expires_in // interval + 1):
        try:
            token = sso_oidc.create_token(
                clientId=client_creds["clientId"],
                clientSecret=client_creds["clientSecret"],
                grantType="urn:ietf:params:oauth:grant-type:device_code",
                deviceCode=device_authorization["deviceCode"],
            )
            break
        except sso_oidc.exceptions.AuthorizationPendingException:
            sleep(interval)

    if not token:
        raise ValueError("SSO authorization took too long and timed out.")

    role_creds = sso.get_role_credentials(
        roleName=AWS_S3_ROLE_NAME,
        accountId=AWS_ACCOUNT_ID,
        accessToken=token["accessToken"],
    )["roleCredentials"]

    return role_creds


def get_read_only_s3_client() -> AWSClient:
    """Return s3 client with read-only access to source/real bucket."""
    return get_read_only_session().client("s3")
