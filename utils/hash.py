from passlib.context import CryptContext

# Configura el contexto de `bcrypt` para el hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para hashear la contraseña
def hash_password(password: str) -> str:
    return pwd_context.hash(password)