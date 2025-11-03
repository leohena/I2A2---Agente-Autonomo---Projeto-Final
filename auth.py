import hashlib
import secrets
from database import get_user_by_email, create_user

def hash_password(password: str) -> str:
    """Cria hash seguro da senha"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${pwd_hash.hex()}"

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha está correta"""
    try:
        salt, pwd_hash = password_hash.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return new_hash.hex() == pwd_hash
    except:
        return False

def authenticate_user(email: str, password: str):
    """Autentica usuário"""
    user = get_user_by_email(email)
    if user and verify_password(password, user['password_hash']):
        return user
    return None

def register_user(email: str, password: str, full_name: str, plan: str):
    """Registra novo usuário"""
    if get_user_by_email(email):
        return None, "Email já cadastrado"
    
    password_hash = hash_password(password)
    user = create_user(email, password_hash, full_name, plan)
    
    if user:
        return user, "Usuário criado com sucesso"
    return None, "Erro ao criar usuário"