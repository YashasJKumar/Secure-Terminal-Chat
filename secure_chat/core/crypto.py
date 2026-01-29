"""
Cryptography module for secure chat application.
Handles RSA key generation, Diffie-Hellman key exchange, AES-GCM encryption, and HMAC.
"""

import os
import time
import hashlib
import hmac
from typing import Tuple, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, dh
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature


class CryptoManager:
    """Manages all cryptographic operations for the chat application."""
    
    # DH parameters (2048-bit prime)
    DH_PARAMETERS = dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())
    
    def __init__(self):
        self.rsa_private_key: Optional[rsa.RSAPrivateKey] = None
        self.rsa_public_key: Optional[rsa.RSAPublicKey] = None
        self.dh_private_key: Optional[dh.DHPrivateKey] = None
        self.dh_public_key: Optional[dh.DHPublicKey] = None
        self.session_key: Optional[bytes] = None
        self.message_counter = 0
        
    def generate_rsa_keypair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Generate RSA key pair for authentication.
        
        Args:
            key_size: Size of RSA key (minimum 2048)
            
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        self.rsa_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.rsa_public_key = self.rsa_private_key.public_key()
        
        private_pem = self.rsa_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = self.rsa_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def load_rsa_private_key(self, pem_data: bytes) -> None:
        """Load RSA private key from PEM data."""
        self.rsa_private_key = serialization.load_pem_private_key(
            pem_data,
            password=None,
            backend=default_backend()
        )
        self.rsa_public_key = self.rsa_private_key.public_key()
    
    def load_peer_rsa_public_key(self, pem_data: bytes) -> rsa.RSAPublicKey:
        """Load peer's RSA public key from PEM data."""
        return serialization.load_pem_public_key(
            pem_data,
            backend=default_backend()
        )
    
    def generate_dh_keypair(self) -> bytes:
        """
        Generate Diffie-Hellman key pair for session key exchange.
        
        Returns:
            DH public key bytes
        """
        self.dh_private_key = self.DH_PARAMETERS.generate_private_key()
        self.dh_public_key = self.dh_private_key.public_key()
        
        # Serialize public key
        return self.dh_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def compute_shared_secret(self, peer_dh_public_key: bytes) -> None:
        """
        Compute shared secret from peer's DH public key and derive session key.
        
        Args:
            peer_dh_public_key: Peer's DH public key in PEM format
        """
        # Load peer's public key
        peer_public_key = serialization.load_pem_public_key(
            peer_dh_public_key,
            backend=default_backend()
        )
        
        # Compute shared secret
        shared_secret = self.dh_private_key.exchange(peer_public_key)
        
        # Derive AES-256 session key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=b'secure_chat_salt',  # In production, use random salt exchanged during handshake
            iterations=100000,
            backend=default_backend()
        )
        self.session_key = kdf.derive(shared_secret)
        self.message_counter = 0
    
    def sign_data(self, data: bytes) -> bytes:
        """
        Sign data with RSA private key.
        
        Args:
            data: Data to sign
            
        Returns:
            Digital signature
        """
        if not self.rsa_private_key:
            raise ValueError("RSA private key not loaded")
        
        signature = self.rsa_private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    def verify_signature(self, data: bytes, signature: bytes, peer_public_key: rsa.RSAPublicKey) -> bool:
        """
        Verify signature using peer's RSA public key.
        
        Args:
            data: Original data
            signature: Signature to verify
            peer_public_key: Peer's RSA public key
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            peer_public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
    
    def encrypt_message(self, plaintext: str) -> bytes:
        """
        Encrypt message using AES-256-GCM.
        
        Args:
            plaintext: Message to encrypt
            
        Returns:
            Encrypted message in format: [IV(12)][Ciphertext][Tag(16)][Timestamp(8)][Counter(4)]
        """
        if not self.session_key:
            raise ValueError("Session key not established")
        
        # Generate random IV (12 bytes for GCM)
        iv = os.urandom(12)
        
        # Add timestamp and counter for replay protection
        timestamp = int(time.time()).to_bytes(8, 'big')
        counter = self.message_counter.to_bytes(4, 'big')
        self.message_counter += 1
        
        # Prepare plaintext with metadata
        message_data = plaintext.encode('utf-8')
        
        # Encrypt with AES-GCM
        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Additional authenticated data (not encrypted but authenticated)
        aad = timestamp + counter
        encryptor.authenticate_additional_data(aad)
        
        ciphertext = encryptor.update(message_data) + encryptor.finalize()
        
        # Return IV + ciphertext + tag + timestamp + counter
        return iv + ciphertext + encryptor.tag + timestamp + counter
    
    def decrypt_message(self, encrypted_data: bytes, expected_counter: int) -> Tuple[str, int]:
        """
        Decrypt message using AES-256-GCM.
        
        Args:
            encrypted_data: Encrypted message
            expected_counter: Expected message counter for replay protection
            
        Returns:
            Tuple of (decrypted message, message counter)
            
        Raises:
            ValueError: If decryption fails or replay attack detected
        """
        if not self.session_key:
            raise ValueError("Session key not established")
        
        if len(encrypted_data) < 36:  # 12 (IV) + 16 (tag) + 8 (timestamp) + 4 (counter) = 40 minimum
            raise ValueError("Invalid encrypted data")
        
        # Parse components
        iv = encrypted_data[:12]
        ciphertext_and_tag = encrypted_data[12:-12]
        timestamp_bytes = encrypted_data[-12:-4]
        counter_bytes = encrypted_data[-4:]
        
        # Extract timestamp and counter
        message_timestamp = int.from_bytes(timestamp_bytes, 'big')
        message_counter = int.from_bytes(counter_bytes, 'big')
        
        # Check for replay attack (timestamp within 60 seconds)
        current_time = int(time.time())
        if abs(current_time - message_timestamp) > 60:
            raise ValueError("Message timestamp too old - possible replay attack")
        
        # Check message counter
        if message_counter < expected_counter:
            raise ValueError("Message counter is old - possible replay attack")
        
        # Split ciphertext and tag
        if len(ciphertext_and_tag) < 16:
            raise ValueError("Invalid encrypted data")
        
        ciphertext = ciphertext_and_tag[:-16]
        tag = ciphertext_and_tag[-16:]
        
        # Decrypt with AES-GCM
        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Add AAD
        aad = timestamp_bytes + counter_bytes
        decryptor.authenticate_additional_data(aad)
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext.decode('utf-8'), message_counter
    
    def compute_hmac(self, data: bytes) -> bytes:
        """
        Compute HMAC-SHA256 for control messages.
        
        Args:
            data: Data to authenticate
            
        Returns:
            HMAC digest
        """
        if not self.session_key:
            raise ValueError("Session key not established")
        
        return hmac.new(self.session_key, data, hashlib.sha256).digest()
    
    def verify_hmac(self, data: bytes, received_hmac: bytes) -> bool:
        """
        Verify HMAC-SHA256.
        
        Args:
            data: Original data
            received_hmac: HMAC to verify
            
        Returns:
            True if HMAC is valid
        """
        expected_hmac = self.compute_hmac(data)
        return hmac.compare_digest(expected_hmac, received_hmac)
    
    def reset_session_key(self) -> None:
        """Reset session key for key rotation."""
        self.session_key = None
        self.dh_private_key = None
        self.dh_public_key = None
        self.message_counter = 0
