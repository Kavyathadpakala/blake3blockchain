import hashlib
from blake3 import blake3

def hash_bytes(data: bytes, algorithm: str) -> str:
    if algorithm == "sha256":
        return hashlib.sha256(data).hexdigest()
    if algorithm == "blake3":
        return blake3(data).hexdigest()
    raise ValueError("Algorithm must be sha256 or blake3.")
