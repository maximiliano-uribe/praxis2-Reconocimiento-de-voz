# services/clave_services.py

import hashlib
import hmac
import os

def guardar_clave(path_archivo_clave: str, clave: str):
    """
    Guarda hash SHA256 de la clave en un archivo de texto.
    """
    hash_clave = hashlib.sha256(clave.encode()).hexdigest()
    with open(path_archivo_clave, "w", encoding="utf-8") as f:
        f.write(hash_clave)
    return True


def verificar_clave(path_archivo_clave: str, clave_ingresada: str) -> bool:
    """
    Verifica una clave comparando hashes con seguridad (HMAC).
    Devuelve True si coincide, False si no.
    """
    if not os.path.exists(path_archivo_clave):
        return False

    with open(path_archivo_clave, "r", encoding="utf-8") as f:
        hash_guardado = f.read().strip()

    hash_ingresada = hashlib.sha256(clave_ingresada.encode("utf-8")).hexdigest()

    return hmac.compare_digest(hash_guardado, hash_ingresada)
