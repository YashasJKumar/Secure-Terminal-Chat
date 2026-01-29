"""
Key management module for secure storage and loading of cryptographic keys.
"""

import os
import json
from pathlib import Path
from typing import Tuple, Optional


class KeyManager:
    """Manages secure storage and loading of RSA keys."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize key manager.
        
        Args:
            base_dir: Base directory for key storage (default: ~/.secure_chat)
        """
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path.home() / '.secure_chat'
        
        self.keys_dir = self.base_dir / 'keys'
        self.logs_dir = self.base_dir / 'logs'
        
        # Create directories if they don't exist
        self.keys_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.logs_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        self.private_key_path = self.keys_dir / 'private_key.pem'
        self.public_key_path = self.keys_dir / 'public_key.pem'
        self.config_path = self.base_dir / 'config.json'
    
    def keys_exist(self) -> bool:
        """Check if RSA key pair exists."""
        return self.private_key_path.exists() and self.public_key_path.exists()
    
    def save_keys(self, private_key_pem: bytes, public_key_pem: bytes) -> None:
        """
        Save RSA key pair to disk.
        
        Args:
            private_key_pem: Private key in PEM format
            public_key_pem: Public key in PEM format
        """
        # Save private key with restricted permissions
        self.private_key_path.write_bytes(private_key_pem)
        os.chmod(self.private_key_path, 0o600)
        
        # Save public key
        self.public_key_path.write_bytes(public_key_pem)
        os.chmod(self.public_key_path, 0o644)
    
    def load_keys(self) -> Tuple[bytes, bytes]:
        """
        Load RSA key pair from disk.
        
        Returns:
            Tuple of (private_key_pem, public_key_pem)
            
        Raises:
            FileNotFoundError: If keys don't exist
        """
        if not self.keys_exist():
            raise FileNotFoundError("Keys not found. Generate keys first.")
        
        private_key_pem = self.private_key_path.read_bytes()
        public_key_pem = self.public_key_path.read_bytes()
        
        return private_key_pem, public_key_pem
    
    def get_public_key(self) -> bytes:
        """
        Get public key.
        
        Returns:
            Public key in PEM format
        """
        if not self.public_key_path.exists():
            raise FileNotFoundError("Public key not found")
        
        return self.public_key_path.read_bytes()
    
    def save_config(self, config: dict) -> None:
        """
        Save configuration to disk.
        
        Args:
            config: Configuration dictionary
        """
        self.config_path.write_text(json.dumps(config, indent=2))
    
    def load_config(self) -> dict:
        """
        Load configuration from disk.
        
        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            return {}
        
        return json.loads(self.config_path.read_text())
    
    def get_log_file_path(self, log_name: str = 'security.log') -> Path:
        """
        Get path to log file.
        
        Args:
            log_name: Name of log file
            
        Returns:
            Path to log file
        """
        return self.logs_dir / log_name
