# -*- coding: utf-8 -*-
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import check_password_hash, generate_password_hash

import logging


class TokenManager:
    secret_key: str
    salt_length: int
    token_timeout: int

    def init_app(self, config):
        self.secret_key = config.SECRET_KEY
        self.salt_length = config.TOKEN_SALT_LENGTH or 32
        self.token_timeout = config.TOKEN_TIMEOUT or 60 * 60 * 24

    def _serializer(self, timeout: int = None):
        if timeout:
            return Serializer(self.secret_key, expires_in=timeout)
        else:
            return Serializer(self.secret_key)

    def generate_token(self, timeout=None):
        return self._serializer(timeout)

    def validate_token(self, token):
        s = self._serializer()
        # noinspection PyBroadException
        try:
            data = s.loads(token)
            return data
        except Exception:
            return False


class PasswordHasher:
    logger: logging.Logger
    hash_mode: str
    salt_length: int

    def __init__(self, config=None):
        if config is not None:
            self.init_app(config)

    def init_app(self, config):
        self.hash_mode = config.PASSWORD_HASH_MODE or "pbkdf2:sha256:100000"
        self.salt_length = config.PASSWORD_SALT_LENGTH or 16

    @staticmethod
    def check_pass_hash(password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, password)

    def generate_pass_hash(self, password: str) -> str:
        return generate_password_hash(password, self.hash_mode, self.salt_length)
