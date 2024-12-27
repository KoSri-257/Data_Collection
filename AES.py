import logging
from Crypto.Cipher import AES
from config import AES_KEY, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

if AES_KEY is None:
    raise ValueError("AES KEY is missing. Please check the environment variable.")

try:
    KEY = bytes.fromhex(AES_KEY)
except ValueError:
    raise ValueError("Invalid KEY format. It should be a valid hexadecimal string.")

if len(KEY) != 32:
    raise ValueError(f"AES KEY length is invalid. Expected 32 bytes, but got {len(KEY)} bytes.")
if not isinstance(KEY, bytes):
    raise TypeError(f"AES KEY must be of type 'bytes', but got {type(KEY)}.")

def encrypt(data: str) -> str:
    try:
        if data is None:
            raise ValueError("Input is missing.")
        if not isinstance(data, str):
            raise TypeError("Input is not a string type.")
        # Convert data to bytes
        data_bytes = data.encode('utf-8')
        block_size = AES.block_size

        # Add PKCS#7 padding
        padding_size = block_size - (len(data_bytes) % block_size)
        padded_data = data_bytes + bytes([padding_size] * padding_size)

        # Encrypt the data
        cipher = AES.new(KEY, AES.MODE_CBC)  
        iv = cipher.iv  # Initialization vector
        encrypted_data = cipher.encrypt(padded_data)
        # Return IV + encrypted data as a hex-encoded string
    except Exception as e:
        raise
    return (iv + encrypted_data).hex()

def decrypt(encrypted_data: str) -> str:
    try:
        if encrypted_data is None:
            raise ValueError("Input is missing.")
        if not isinstance(encrypted_data, str):
            raise TypeError("Input must be a string.")

        # Convert hex-encoded string back to bytes
        encrypted_bytes = bytes.fromhex(encrypted_data)

        block_size = AES.block_size
        iv = encrypted_bytes[:block_size]  # Extract the IV (first block_size bytes)
        encrypted_content = encrypted_bytes[block_size:]  # Extract the encrypted content

        # Initialize the cipher for decryption
        cipher = AES.new(KEY, AES.MODE_CBC, iv=iv)
        decrypted_padded_data = cipher.decrypt(encrypted_content)

        # Remove PKCS#7 padding
        padding_size = decrypted_padded_data[-1]
        if padding_size < 1 or padding_size > block_size:
            raise ValueError("Invalid padding size.")
        decrypted_data = decrypted_padded_data[:-padding_size]  # Remove padding

        # Log the decrypted data
        logger.info(f"Decrypted data: {decrypted_data.decode('utf-8')}")

    except Exception as e:
        raise
    return decrypted_data.decode('utf-8')
