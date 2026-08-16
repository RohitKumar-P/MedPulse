import os
import base64
import json
from pathlib import Path

from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_key = os.getenv("AEGIS_ENCRYPTION_KEY")

if not _key:
    raise RuntimeError("AEGIS_ENCRYPTION_KEY is not configured")

KEY = base64.urlsafe_b64decode(_key)

if len(KEY) != 32:
    raise RuntimeError("AEGIS_ENCRYPTION_KEY must decode to 32 bytes")


def encrypt_value(value):
    if value is None:
        return None

    plaintext = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":")
    ).encode("utf-8")

    nonce = os.urandom(12)

    ciphertext = AESGCM(KEY).encrypt(
        nonce,
        plaintext,
        None
    )

    return base64.b64encode(
        nonce + ciphertext
    ).decode("ascii")


def decrypt_value(value):
    if value is None:
        return None

    raw = base64.b64decode(value.encode("ascii"))

    nonce = raw[:12]
    ciphertext = raw[12:]

    plaintext = AESGCM(KEY).decrypt(
        nonce,
        ciphertext,
        None
    )

    return json.loads(
        plaintext.decode("utf-8")
    )
