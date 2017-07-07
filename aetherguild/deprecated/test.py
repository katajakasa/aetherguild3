from aetherguild.deprecated.hash import register_hash
register_hash()
from passlib.hash import aethery1, aethery2
from dynaconf import settings
from passlib.context import CryptContext

settings.configure('aetherguild.settings')
pwd_context = CryptContext(schemes=["argon2", "aethery2", "aethery1"], deprecated="auto")


print(pwd_context.hash("kek"))
print(aethery1.hash("kek"))
print(aethery2.hash("kek"))
print(pwd_context.verify(
    "kek", "$aethery-sha256$MjM1N2RiNTd1YjV5YXcwbjNYRSVCTj0vNEFXVu+/vUdWQg==$dae5cf5a48160711f7aea2f1b15f1cd244d20d6d"))

