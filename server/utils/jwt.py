import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from .exceptions import e_expired_token, e_invalid_token
from config import setting


# Function to load private key
def load_private_key(pk_file_path: str, password: str | None = ""):
    f = open(pk_file_path, "r")
    private_key = f.read()
    f.close()
    return serialization.load_ssh_private_key(
        private_key.encode(), password=bytes(password.encode())
    )


# Function to load public key
def load_public_key(pk_file_path: str):
    f = open(pk_file_path, "r")
    public_key = f.read()
    f.close()
    return serialization.load_ssh_public_key(public_key.encode())


pu = load_public_key(pk_file_path="server\\utils\\keys\\id_rsa.pub")
pr = load_private_key(pk_file_path="server\\utils\\keys\\id_rsa")

# Loading the rsa keys
pu = load_public_key(pk_file_path=setting.PUBLIC_KEY)
pr = load_private_key(pk_file_path=setting.PRIVATE_KEY)


# Function to create the JWT
def create_access_token(uid: str, email: str, role: str):
    payload = {
        "uid": uid,
        "email": email,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=600),
    }
    return jwt.encode(payload, key=pr, algorithm=setting.ALGORITHM)


# Function to validate the JWT
def validate_access_token(access_token: str):
    # Using Expired Signature from pyjwt to validate the signature expiration error
    try:
        payload = jwt.decode(access_token, key=pu, algorithms=setting.ALGORITHM)
        return payload

    except ExpiredSignatureError as e:
        raise e_expired_token()

    except InvalidTokenError as e:
        raise e_invalid_token()
