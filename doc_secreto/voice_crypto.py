import hashlib
import base64
import soundfile as sf
from cryptography.fernet import Fernet

def derive_key_from_voice(wav_path: str):
    data, sr = sf.read(wav_path)
    audiobytes = data.tobytes()
    digest = hashlib.sha256(audiobytes).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_with_voice(wav_path: str, texto: str):
    key = derive_key_from_voice(wav_path)
    f = Fernet(key)
    return f.encrypt(texto.encode("utf-8"))


def decrypt_with_voice(wav_path: str, encrypted_bytes: bytes):
    key = derive_key_from_voice(wav_path)
    f = Fernet(key)
    return f.decrypt(encrypted_bytes).decode("utf-8")
