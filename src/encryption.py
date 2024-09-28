import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key(password: str, salt: bytes, length: int = 32) -> bytes:
    """Derive a fixed-length key from a password using PBKDF2HMAC.

    Args:
        password (str): The password from which to derive the key.
        salt (bytes): A random salt to make the key derivation more secure.
        length (int): The length of the desired key in bytes.
            Default is 32 bytes (256 bits).

    Returns:
        bytes: The derived key of the specified length.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    return kdf.derive(password.encode())


def encrypt(message: str, password: str) -> str:
    """Encrypts a message using AES encryption and a password.

    The password is used to derive a key, and the message is padded and
    encrypted with AES in CBC mode. A random salt and IV are used, and the
    result is returned as a base64-encoded string.

    Args:
        message (str): The plaintext message to encrypt.
        password (str): The password used to derive the encryption key.

    Returns:
        str: The base64-encoded ciphertext including the salt and IV.
    """
    salt = os.urandom(16)# Generate a random 16-byte salt
    key = derive_key(password, salt)  # Derive a 256-bit key from the password
    iv = os.urandom(16)  # Generate a random 16-byte IV for AES

    # Pad the message to a multiple of the AES block size (128 bits)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_message = padder.update(message.encode()) + padder.finalize()

    # Encrypt the padded message using AES-CBC
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_message) + encryptor.finalize()

    # Return the salt, IV, and ciphertext as a base64-encoded string
    return base64.b64encode(salt + iv + ciphertext).decode()


def decrypt(encrypted_message: str, password: str) -> str:
    """Decrypt a base64-encoded AES-encrypted message using a password.

    The salt and IV are extracted from the encrypted message, and the password
    is used to derive the decryption key. The message is then decrypted and
    unpadded to retrieve the original plaintext.

    Args:
        encrypted_message (str): The base64-encoded encrypted message,
            containing the salt, IV, and ciphertext.
        password (str): The password used to derive the decryption key.

    Returns:
        str: The decrypted plaintext message.
    """
    encrypted_data = base64.b64decode(encrypted_message)

    # Extract the salt (first 16 bytes), IV (next 16 bytes),
    # and ciphertext (the rest)
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]

    # Derive the key using the same salt
    key = derive_key(password, salt)

    # Decrypt the ciphertext using AES-CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_message = decryptor.update(ciphertext) + decryptor.finalize()

    # Unpad the decrypted message to retrieve the original plaintext
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    message = unpadder.update(padded_message) + unpadder.finalize()

    return message.decode()
