import hashlib
import os

# Email Hashing Algorithm
def hash_email(email):
    salt = os.getenv('EMAIL_HASH_SALT')
    return hashlib.sha256((email + salt).encode()).hexdigest()