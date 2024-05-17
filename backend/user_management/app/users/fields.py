from django.db import models
from cryptography.fernet import Fernet
import base64
import os
import hashlib

class EncryptedField(models.CharField):
    def __init__(self, *args, **kwargs):
        secret_key = os.environ.get('TOTP_SECRET_KEY')
        if not secret_key:
            raise ValueError("No TOTP_SECRET_KEY environment variable")
        derived_key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode('utf-8')).digest())
        self.cipher = Fernet(derived_key)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.cipher.decrypt(value.encode('utf-8')).decode('utf-8')

    def get_prep_value(self, value):
        if value is None:
            return value
        return self.cipher.encrypt(value.encode('utf-8')).decode('utf-8')