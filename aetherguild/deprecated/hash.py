from passlib.utils.handlers import GenericHandler, HasSalt, parse_mc2, render_mc2, BASE64_CHARS
from passlib.registry import register_crypt_handler_path
from passlib.utils.compat import str_to_uascii
from hashlib import sha1, sha256
from base64 import b64encode, b64decode
from dynaconf import settings


class AetherOldHash(HasSalt, GenericHandler):
    name = "aethery2"
    ident = "$aethery-sha256$"
    setting_kwds = ("salt", )

    def to_string(self):
        return render_mc2(self.ident, self.salt, self.checksum)

    @classmethod
    def from_string(cls, _hash, **context):
        salt, chk = parse_mc2(_hash, cls.ident, handler=cls)
        return cls(salt=salt, checksum=chk)

    @classmethod
    def _generate_salt(cls):
        return b64encode(settings.OLD_PW_SALT.encode('utf-8')).decode('utf-8')

    def _calc_checksum(self, secret):
        m_str = secret + b64decode(self.salt).decode('utf-8')
        m_hash = sha256(m_str.encode('utf-8'))
        return str_to_uascii(m_hash.hexdigest())

    @classmethod
    def format_hash(cls, _checksum):
        return render_mc2(cls.ident, cls._generate_salt(), _checksum)


class AetherReallyOldHash(HasSalt, GenericHandler):
    name = "aethery1"
    ident = "$aethery-sha1$"
    setting_kwds = ("salt", )
    min_salt_size = 12
    max_salt_size = 12
    salt_chars = BASE64_CHARS

    def to_string(self):
        return render_mc2(self.ident, self.salt, self.checksum)

    @classmethod
    def from_string(cls, _hash, **context):
        salt, chk = parse_mc2(_hash, cls.ident, handler=cls)
        return cls(salt=salt, checksum=chk)

    def _generate_salt(cls):
        salt = super(AetherReallyOldHash, self)._generate_salt()
        return b64encode(salt)

    def _calc_checksum(self, secret):
        m_salt = b64decode(self.salt).decode('utf-8')
        m_hash = sha1(m_salt + sha1(secret.encode('utf-8')).digest())
        return str_to_uascii(m_hash.hexdigest())

    @classmethod
    def format_hash(cls, _salt, _checksum):
        return render_mc2(cls.ident, b64encode(_salt).decode('utf-8'), _checksum)


def register_hash():
    register_crypt_handler_path("aethery1", "aetherguild.deprecated.hash:AetherReallyOldHash")
    register_crypt_handler_path("aethery2", "aetherguild.deprecated.hash:AetherOldHash")
