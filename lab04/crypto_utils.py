from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util import Counter
from Crypto.Hash import SHA1, SHA256
from Crypto.Protocol.KDF import PBKDF2
from config import SYSTEM_PEPPER

def hash_password_sha1(password: str) -> str:
    """Hash password using SHA1 to hex string."""
    h = SHA1.new()
    h.update(password.encode('utf-8'))
    return h.hexdigest().upper()

system_pepper = SYSTEM_PEPPER['pepper']

def generate_deterministic_rsa(password: str, manv: str) -> tuple[bytes, bytes]:
    """
    Generates a deterministic RSA 2048 keypair based on Password + MANV + Pepper.
    Returns (private_key_pem, public_key_pem).
    """
    # Tạo seed sinh keypair
    raw_material = f"{password}|{manv}|{system_pepper}"
    safe_salt = f"{manv}|{system_pepper}".encode('utf-8')
    seed = PBKDF2(raw_material, safe_salt, dkLen=32, count=100000, hmac_hash_module=SHA256)
    
    # Setup AES-CTR as DRBG (Deterministic Random Bit Generator)
    ctr = Counter.new(128, initial_value=0)
    cipher = AES.new(seed, AES.MODE_CTR, counter=ctr)
    
    def deterministic_randfunc(n):
        return cipher.encrypt(b'\x00' * n)
    
    # Sinh keypair RSA 2048 bit sử dụng DRBG
    key = RSA.generate(2048, randfunc=deterministic_randfunc)
    
    private_key_pem = key.export_key()
    public_key_pem = key.publickey().export_key()
    
    return private_key_pem, public_key_pem

def rsa_encrypt(public_key_pem: bytes, plaintext: str) -> str:
    """Encrypt plaintext using RSA Public Key, return Base64 string."""
    pub_key = RSA.import_key(public_key_pem)
    cipher = PKCS1_OAEP.new(pub_key, hashAlgo=SHA256)
    ciphertext = cipher.encrypt(plaintext.encode('utf-8'))
    return ciphertext

def rsa_decrypt(private_key_pem: bytes, ciphertext: str) -> str:
    """Decrypt Base64 ciphertext using RSA Private Key, return plaintext string."""
    priv_key = RSA.import_key(private_key_pem)
    cipher = PKCS1_OAEP.new(priv_key, hashAlgo=SHA256)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.decode('utf-8')


# # =========================
# # DEMO
# # =========================

# password = "Abcd123!"
# manv = "NV01"

# plaintext = "9.5"

# # Hash password
# password_hash = hash_password_sha1(password)

# print("PASSWORD HASH:")
# print(password_hash)

# # Generate deterministic RSA keypair
# private_key, public_key = generate_deterministic_rsa(
#     password,
#     manv
# )

# print("\nPUBLIC KEY:")
# print(public_key.decode())

# print("\nPRIVATE KEY:")
# print(private_key.decode())

# # Encrypt
# ciphertext = rsa_encrypt(
#     public_key,
#     plaintext
# )

# print("\nENCRYPTED:")
# print(ciphertext)

# # Decrypt
# decrypted_text = rsa_decrypt(
#     private_key,
#     ciphertext
# )

# print("\nDECRYPTED:")
# print(decrypted_text)