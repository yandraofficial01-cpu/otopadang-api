from passlib.context import CryptContext

# Mesin buat ngacak password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """Dipake pas register. Ubah '123456' jadi '$2b$12$...' """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Dipake pas login. Ngecek '123456' == '$2b$12$...' """
    return pwd_context.verify(plain_password, hashed_password)