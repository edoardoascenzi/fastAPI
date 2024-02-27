from passlib.context import CryptContext
psw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str) -> str:
    return psw_context.hash(password)

def verify(plainPassword: str, hashedPassword: str ) -> bool:
    return psw_context.verify(plainPassword, hashedPassword)
