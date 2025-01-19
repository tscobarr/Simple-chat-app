from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt_message(message, key):
    iv = get_random_bytes(16)  # Generate a random IV
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(message.encode(), AES.block_size)
    return iv + cipher.encrypt(padded_data)  # Prepend IV to the ciphertext

def decrypt_message(ciphertext, key):
    iv = ciphertext[:16]  # Extract the IV from the beginning
    ciphertext = ciphertext[16:]  # Extract the actual ciphertext
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = cipher.decrypt(ciphertext)
    return unpad(padded_data, AES.block_size).decode()