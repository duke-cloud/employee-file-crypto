from cryptography.fernet import Fernet
import os

KEY = Fernet.generate_key()  # In production, save and reuse the same key
cipher = Fernet(KEY)




from django.conf import settings

cipher = settings.FERNET_CIPHER

# Encrypt
#encrypted = cipher.encrypt(data)

# Decrypt
#decrypted = cipher.decrypt(encrypted_data)


def encrypt_file(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    encrypted_data = cipher.encrypt(data)
    encrypted_path = file_path + '.enc'
    with open(encrypted_path, 'wb') as f:
        f.write(encrypted_data)
    return encrypted_path

def decrypt_file(encrypted_path):
    with open(encrypted_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    decrypted_path = encrypted_path.replace('.enc', '.dec')
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_data)
    return decrypted_path




