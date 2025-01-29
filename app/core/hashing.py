import bcrypt


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password.encode("utf-8"))
