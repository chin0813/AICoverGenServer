# app/utils.py

import hashlib

def get_hash(filepath):
    with open(filepath, 'rb') as f:
        file_hash = hashlib.blake2b()
        while chunk := f.read(8192):
            file_hash.update(chunk)

    return file_hash.hexdigest()[:11]