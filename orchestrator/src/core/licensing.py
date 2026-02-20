import os
import json
import base64
import time
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# --- CONFIGURATION (In Prod, inject PUBLIC_KEY via Env/Build) ---
# This is the PUBLIC key corresponding to the Private key you keep offline.
# I will generate a pair for you now to embed.
DEFAULT_PUBLIC_KEY_PEM = b"""
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAnhfrubIeVcSD391rI6ClleZF7bC/m8CeKOORBozj3po=
-----END PUBLIC KEY-----
"""

# DEVELOPMENT OVERRIDE: If this is set, we bypass crypto check for "mock_key"
DEV_MODE = os.getenv("ENV_MODE", "dev") == "dev"

class LicenseManager:
    def __init__(self, public_key_pem: bytes = None):
        self.public_key_pem = public_key_pem or os.getenv("LICENSE_PUBLIC_KEY", "").encode() or DEFAULT_PUBLIC_KEY_PEM
        try:
            if self.public_key_pem:
                self.public_key = serialization.load_pem_public_key(self.public_key_pem)
            else:
                self.public_key = None
        except Exception:
            self.public_key = None

    def verify_license_key(self, license_key: str) -> dict:
        """
        Verifies a base64 encoded license key.
        Format: Base64( Signature(64 bytes) + JSON_Payload )
        """
        # DEV BYPASS
        if DEV_MODE and license_key == "mock_dev_key":
             return {"valid": True, "data": {"tier": "DEV", "features": ["swarm", "voice", "api"], "sub": "dev@local"}}

        if not self.public_key:
            # Fallback for dev mode only if strictly allowed
            if os.getenv("ENV_MODE") == "dev":
                return {"valid": True, "tier": "DEV_UNLIMITED", "features": ["all"]}
            return {"valid": False, "error": "System Public Key Missing"}

        try:
            decoded = base64.b64decode(license_key)
            if len(decoded) < 64:
                return {"valid": False, "error": "Invalid Key Format"}

            signature = decoded[:64]
            payload_bytes = decoded[64:]

            # 1. Verify Signature
            self.public_key.verify(signature, payload_bytes)

            # 2. Parse Payload
            data = json.loads(payload_bytes.decode())
            
            # 3. Check Expiry
            if "exp" in data and data["exp"] < time.time():
                return {"valid": False, "error": "License Expired"}

            return {"valid": True, "data": data}

        except Exception as e:
            return {"valid": False, "error": f"Verification Failed: {str(e)}"}

# Singleton
license_manager = LicenseManager()
