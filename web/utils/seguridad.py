import hashlib, hmac, os
from config import CLAVE_FILE

def guardar_clave_hash(clave):
    h = hashlib.sha256(clave.encode()).hexdigest()
    with open(CLAVE_FILE, "w") as f:
        f.write(h)

def verificar_hash(clave):
    if not os.path.exists(CLAVE_FILE):
        return False

    with open(CLAVE_FILE, "r") as f:
        hash_guardado = f.read().strip()

    h = hashlib.sha256(clave.encode()).hexdigest()
    return hmac.compare_digest(hash_guardado, h)
