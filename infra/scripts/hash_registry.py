from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import json
import base64
import time
import sys

def generate_keys():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    print("\n=== SAVE THIS PRIVATE KEY SECURELY (OFFLINE) ===")
    print(priv_pem.decode())
    print("\n=== EMBED THIS PUBLIC KEY IN APP ===")
    print(pub_pem.decode())
    return private_key

def mint_license(private_key, customer_email, tier="PRO", days=365):
    payload = {
        "sub": customer_email,
        "tier": tier,
        "exp": int(time.time() + (days * 86400)),
        "features": ["swarm", "voice", "api"] if tier == "PRO" else ["swarm"]
    }
    payload_bytes = json.dumps(payload).encode()
    signature = private_key.sign(payload_bytes)
    
    license_key = base64.b64encode(signature + payload_bytes).decode()
    return license_key

if __name__ == "__main__":
    print("Generating Sovereign Keys...")
    priv = generate_keys()
    
    print("\n--- TEST LICENSE (1 Year) ---")
    print(mint_license(priv, "test@realms2riches.ai"))
