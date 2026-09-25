"""
crypto_utils.py
----------------
Core encryption/decryption logic for the Secure File Encryption & Decryption Tool.

Algorithm:  AES-256-GCM (Authenticated Encryption)
Key Derivation: PBKDF2-HMAC-SHA256 (200,000 iterations) from a user password
Integrity: GCM's built-in authentication tag detects any tampering or corruption

Encrypted file format (all binary, written in this order):
    [ 16 bytes ]  MAGIC HEADER  b"SFETv1_________" (padded/truncated to 16 bytes)
    [ 16 bytes ]  salt          (random, used for key derivation)
    [ 12 bytes ]  nonce         (random, required by AES-GCM)
    [ N  bytes ]  ciphertext    (includes the 16-byte GCM authentication tag)
"""

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

MAGIC = b"SFETv1__________"[:16]   # 16-byte format signature
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32          # 32 bytes = AES-256
PBKDF2_ITERATIONS = 200_000


class DecryptionError(Exception):
    """Raised when a file cannot be decrypted (wrong password or corrupted/tampered file)."""
    pass


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit AES key from a password + salt using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_bytes(plaintext: bytes, password: str) -> bytes:
    """Encrypt raw bytes with a password. Returns the full encrypted file contents."""
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    return MAGIC + salt + nonce + ciphertext


def decrypt_bytes(encrypted_data: bytes, password: str) -> bytes:
    """Decrypt bytes produced by encrypt_bytes(). Raises DecryptionError on failure."""
    if len(encrypted_data) < 16 + SALT_SIZE + NONCE_SIZE:
        raise DecryptionError("File is too short or not a valid encrypted file.")

    header = encrypted_data[:16]
    if header != MAGIC:
        raise DecryptionError("File format not recognized (missing/invalid header).")

    salt = encrypted_data[16:16 + SALT_SIZE]
    nonce = encrypted_data[16 + SALT_SIZE:16 + SALT_SIZE + NONCE_SIZE]
    ciphertext = encrypted_data[16 + SALT_SIZE + NONCE_SIZE:]

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    except InvalidTag:
        raise DecryptionError("Incorrect password or the file has been corrupted/tampered with.")

    return plaintext


def encrypt_file(input_path: str, output_path: str, password: str) -> None:
    with open(input_path, "rb") as f:
        data = f.read()
    encrypted = encrypt_bytes(data, password)
    with open(output_path, "wb") as f:
        f.write(encrypted)


def decrypt_file(input_path: str, output_path: str, password: str) -> None:
    with open(input_path, "rb") as f:
        data = f.read()
    decrypted = decrypt_bytes(data, password)
    with open(output_path, "wb") as f:
        f.write(decrypted)
