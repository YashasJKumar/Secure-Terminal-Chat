"""
Logging module for security events and audit trail.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class SecurityLogger:
    """Logs security events without logging message content."""
    
    def __init__(self, log_file: Path):
        """
        Initialize security logger.
        
        Args:
            log_file: Path to log file
        """
        self.logger = logging.getLogger('secure_chat')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)
        
        # Format: [Timestamp][Event_Type][Peer_Info][Status]
        formatter = logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def log_key_generation(self):
        """Log RSA key pair generation."""
        self.logger.info("KEY_GENERATION: RSA key pair generated")
    
    def log_key_loaded(self):
        """Log RSA key pair loaded from disk."""
        self.logger.info("KEY_LOADED: RSA key pair loaded from storage")
    
    def log_peer_discovered(self, peer_id: str, address: str):
        """Log peer discovery."""
        self.logger.info(f"PEER_DISCOVERED: peer_id={peer_id}, address={address}")
    
    def log_invitation_sent(self, peer_id: str, address: str):
        """Log connection invitation sent."""
        self.logger.info(f"INVITATION_SENT: peer_id={peer_id}, address={address}")
    
    def log_invitation_received(self, peer_id: str, address: str):
        """Log connection invitation received."""
        self.logger.info(f"INVITATION_RECEIVED: peer_id={peer_id}, address={address}")
    
    def log_invitation_accepted(self, peer_id: str):
        """Log invitation acceptance."""
        self.logger.info(f"INVITATION_ACCEPTED: peer_id={peer_id}")
    
    def log_invitation_rejected(self, peer_id: str):
        """Log invitation rejection."""
        self.logger.info(f"INVITATION_REJECTED: peer_id={peer_id}")
    
    def log_key_exchange_started(self, peer_id: str):
        """Log start of key exchange."""
        self.logger.info(f"KEY_EXCHANGE_STARTED: peer_id={peer_id}")
    
    def log_key_exchange_completed(self, peer_id: str):
        """Log successful key exchange."""
        self.logger.info(f"KEY_EXCHANGE_COMPLETED: peer_id={peer_id}, status=SUCCESS")
    
    def log_key_exchange_failed(self, peer_id: str, reason: str):
        """Log failed key exchange."""
        self.logger.error(f"KEY_EXCHANGE_FAILED: peer_id={peer_id}, reason={reason}")
    
    def log_connection_established(self, peer_id: str, address: str):
        """Log successful connection establishment."""
        self.logger.info(f"CONNECTION_ESTABLISHED: peer_id={peer_id}, address={address}")
    
    def log_connection_failed(self, peer_id: str, reason: str):
        """Log failed connection attempt."""
        self.logger.error(f"CONNECTION_FAILED: peer_id={peer_id}, reason={reason}")
    
    def log_message_sent(self, peer_id: str):
        """Log message sent (without content)."""
        self.logger.info(f"MESSAGE_SENT: peer_id={peer_id}")
    
    def log_message_received(self, peer_id: str):
        """Log message received (without content)."""
        self.logger.info(f"MESSAGE_RECEIVED: peer_id={peer_id}")
    
    def log_key_rotation(self, peer_id: str):
        """Log session key rotation."""
        self.logger.info(f"KEY_ROTATION: peer_id={peer_id}")
    
    def log_session_timeout(self, peer_id: str):
        """Log session timeout."""
        self.logger.warning(f"SESSION_TIMEOUT: peer_id={peer_id}")
    
    def log_disconnection(self, peer_id: str, reason: str = "user_request"):
        """Log session disconnection."""
        self.logger.info(f"DISCONNECTION: peer_id={peer_id}, reason={reason}")
    
    def log_replay_attack_detected(self, peer_id: str):
        """Log detected replay attack."""
        self.logger.error(f"REPLAY_ATTACK_DETECTED: peer_id={peer_id}")
    
    def log_signature_verification_failed(self, peer_id: str):
        """Log failed signature verification."""
        self.logger.error(f"SIGNATURE_VERIFICATION_FAILED: peer_id={peer_id}")
    
    def log_decryption_failed(self, peer_id: str):
        """Log failed message decryption."""
        self.logger.error(f"DECRYPTION_FAILED: peer_id={peer_id}")
