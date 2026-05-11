from pwdlib import PasswordHash

def get_password_hash(password: str) -> str:
    password_hash = PasswordHash.recommended()
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    password_hash = PasswordHash.recommended()
    return password_hash.verify(password, hashed_password)
