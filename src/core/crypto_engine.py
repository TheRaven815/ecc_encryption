from cryptography.hazmat.primitives.asymmetric import ec, ed25519, x25519
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
import base64

class ECCEngine:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_keys(self, curve_name: str, password: bytes = None):
        """Generates ECC keys based on the selected curve."""
        try:
            if "SECP256R1" in curve_name:
                self.private_key = ec.generate_private_key(ec.SECP256R1())
            elif "SECP384R1" in curve_name:
                self.private_key = ec.generate_private_key(ec.SECP384R1())
            elif "SECP521R1" in curve_name:
                self.private_key = ec.generate_private_key(ec.SECP521R1())
            elif "Ed25519" in curve_name:
                self.private_key = ed25519.Ed25519PrivateKey.generate()
            elif "X25519" in curve_name:
                self.private_key = x25519.X25519PrivateKey.generate()
            else:
                raise ValueError(f"Unsupported curve: {curve_name}")

            self.public_key = self.private_key.public_key()
            return self.export_keys(password)
        except Exception as e:
            raise RuntimeError(f"Key generation failed: {str(e)}")

    def export_keys(self, password: bytes = None):
        """Exports the current keys in PEM format."""
        if not self.private_key:
            return None, None

        enc_alg = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()

        priv_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=enc_alg
        )
        pub_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return priv_pem.decode('utf-8'), pub_pem.decode('utf-8')

    def load_private_key(self, pem_data: bytes, password: bytes = None):
        """Loads a private key from PEM data and derives the public key."""
        try:
            self.private_key = serialization.load_pem_private_key(pem_data, password=password)
            self.public_key = self.private_key.public_key()
            return self.export_keys(password)
        except Exception as e:
            raise RuntimeError(f"Failed to load private key: {str(e)}")

    def load_public_key(self, pem_data: bytes):
        """Loads a public key from PEM data."""
        try:
            self.public_key = serialization.load_pem_public_key(pem_data)
            return pem_data.decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Failed to load public key: {str(e)}")

    def sign_message(self, message: str):
        """Signs a message using the current private key."""
        if not self.private_key:
            raise ValueError("Private key is not loaded.")

        msg_bytes = message.encode('utf-8')

        try:
            if isinstance(self.private_key, ec.EllipticCurvePrivateKey):
                signature = self.private_key.sign(msg_bytes, ec.ECDSA(hashes.SHA256()))
            elif isinstance(self.private_key, ed25519.Ed25519PrivateKey):
                signature = self.private_key.sign(msg_bytes)
            elif isinstance(self.private_key, x25519.X25519PrivateKey):
                raise ValueError("X25519 is for Key Exchange, not Digital Signatures.")
            else:
                raise ValueError("Unsupported key type for signing.")

            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Signing failed: {str(e)}")

    def verify_signature(self, message: str, signature_base64: str):
        """Verifies a signature using the current public key."""
        if not self.public_key:
            raise ValueError("Public key is not loaded.")

        try:
            msg_bytes = message.encode('utf-8')
            signature = base64.b64decode(signature_base64)

            if isinstance(self.public_key, ec.EllipticCurvePublicKey):
                self.public_key.verify(signature, msg_bytes, ec.ECDSA(hashes.SHA256()))
            elif isinstance(self.public_key, ed25519.Ed25519PublicKey):
                self.public_key.verify(signature, msg_bytes)
            else:
                raise ValueError("Unsupported public key type for verification.")
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            raise RuntimeError(f"Verification failed: {str(e)}")
