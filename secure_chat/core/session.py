"""
Session management module for handling secure connections and key rotation.
"""

import socket
import json
import time
import threading
from enum import Enum
from typing import Optional, Callable
from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from .crypto import CryptoManager
from .network import NetworkManager, PeerInfo


class SessionState(Enum):
    """States of a chat session."""
    DISCONNECTED = "disconnected"
    INVITATION_SENT = "invitation_sent"
    INVITATION_RECEIVED = "invitation_received"
    KEY_EXCHANGE = "key_exchange"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class SessionInfo:
    """Information about a chat session."""
    peer_id: str
    peer_address: str
    state: SessionState
    established_at: Optional[float] = None
    last_activity: Optional[float] = None
    messages_sent: int = 0
    key_rotation_at: Optional[float] = None


class SessionManager:
    """Manages secure chat sessions with peers."""
    
    MESSAGES_BEFORE_REKEY = 100
    TIME_BEFORE_REKEY = 1800  # 30 minutes
    SESSION_TIMEOUT = 1800  # 30 minutes
    
    def __init__(self, crypto: CryptoManager, network: NetworkManager):
        """
        Initialize session manager.
        
        Args:
            crypto: Crypto manager instance
            network: Network manager instance
        """
        self.crypto = crypto
        self.network = network
        self.session: Optional[SessionInfo] = None
        self.peer_socket: Optional[socket.socket] = None
        self.peer_public_key: Optional[bytes] = None
        self.receive_counter = 0
        self.on_message_received: Optional[Callable[[str], None]] = None
        self.on_state_changed: Optional[Callable[[SessionState], None]] = None
        self.on_invitation_received: Optional[Callable[[str, str], None]] = None
        self.running = False
        self.receive_thread: Optional[threading.Thread] = None
        self.rekey_lock = threading.Lock()  # Lock to prevent concurrent rekeys
    
    def send_invitation(self, peer: PeerInfo) -> bool:
        """
        Send connection invitation to a peer.
        
        Args:
            peer: Peer information
            
        Returns:
            True on success
        """
        # Connect to peer
        sock = self.network.connect_to_peer(peer.address, peer.port)
        if not sock:
            return False
        
        # Send invitation message
        invitation = {
            'type': 'invitation',
            'peer_id': self.network.peer_id,
            'public_key': self.crypto.rsa_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8'),
            'timestamp': int(time.time())
        }
        
        # Sign the invitation
        invitation_data = json.dumps({
            'peer_id': invitation['peer_id'],
            'timestamp': invitation['timestamp']
        }).encode('utf-8')
        signature = self.crypto.sign_data(invitation_data)
        invitation['signature'] = signature.hex()
        
        message = json.dumps(invitation).encode('utf-8')
        
        if not self.network.send_message(sock, message):
            sock.close()
            return False
        
        # Wait for response
        response_data = self.network.receive_message(sock, timeout=10.0)
        if not response_data:
            sock.close()
            return False
        
        try:
            response = json.loads(response_data.decode('utf-8'))
            
            if response['type'] == 'invitation_accepted':
                # Store peer info and socket
                self.peer_socket = sock
                self.peer_public_key = peer.public_key
                self.session = SessionInfo(
                    peer_id=peer.peer_id,
                    peer_address=peer.address,
                    state=SessionState.KEY_EXCHANGE
                )
                self._update_state(SessionState.KEY_EXCHANGE)
                
                # Start key exchange
                return self._perform_key_exchange(initiator=True)
            else:
                sock.close()
                return False
        except Exception as e:
            print(f"Error processing invitation response: {e}")
            sock.close()
            return False
    
    def handle_invitation(self, sock: socket.socket, invitation_data: bytes) -> bool:
        """
        Handle incoming invitation.
        
        Args:
            sock: Socket from peer
            invitation_data: Invitation message data
            
        Returns:
            True if invitation should be accepted (decided by callback)
        """
        try:
            invitation = json.loads(invitation_data.decode('utf-8'))
            
            if invitation['type'] != 'invitation':
                return False
            
            # Verify signature
            peer_id = invitation['peer_id']
            timestamp = invitation['timestamp']
            peer_public_key_pem = invitation['public_key'].encode('utf-8')
            signature = bytes.fromhex(invitation['signature'])
            
            # Load peer's public key
            peer_public_key = serialization.load_pem_public_key(
                peer_public_key_pem,
                backend=default_backend()
            )
            
            # Verify signature
            invitation_data_to_verify = json.dumps({
                'peer_id': peer_id,
                'timestamp': timestamp
            }).encode('utf-8')
            
            if not self.crypto.verify_signature(invitation_data_to_verify, signature, peer_public_key):
                return False
            
            # Check timestamp (within 60 seconds)
            if abs(time.time() - timestamp) > 60:
                return False
            
            # Check if there's already a pending invitation
            if hasattr(self, 'pending_invitation'):
                # Close the old socket
                try:
                    self.pending_invitation['socket'].close()
                except:
                    pass
            
            # Callback to user for acceptance
            if self.on_invitation_received:
                self.on_invitation_received(peer_id, sock.getpeername()[0])
            
            # Store for later acceptance
            self.pending_invitation = {
                'socket': sock,
                'peer_id': peer_id,
                'peer_public_key': peer_public_key_pem
            }
            
            return True
        except Exception as e:
            print(f"Error handling invitation: {e}")
            return False
    
    def accept_invitation(self) -> bool:
        """Accept pending invitation."""
        if not hasattr(self, 'pending_invitation'):
            return False
        
        invitation = self.pending_invitation
        sock = invitation['socket']
        
        # Send acceptance
        response = {
            'type': 'invitation_accepted',
            'peer_id': self.network.peer_id
        }
        
        if not self.network.send_message(sock, json.dumps(response).encode('utf-8')):
            return False
        
        # Store peer info
        self.peer_socket = sock
        self.peer_public_key = invitation['peer_public_key']
        self.session = SessionInfo(
            peer_id=invitation['peer_id'],
            peer_address=sock.getpeername()[0],
            state=SessionState.KEY_EXCHANGE
        )
        self._update_state(SessionState.KEY_EXCHANGE)
        
        # Perform key exchange
        return self._perform_key_exchange(initiator=False)
    
    def reject_invitation(self) -> bool:
        """Reject pending invitation."""
        if not hasattr(self, 'pending_invitation'):
            return False
        
        invitation = self.pending_invitation
        sock = invitation['socket']
        
        response = {
            'type': 'invitation_rejected'
        }
        
        self.network.send_message(sock, json.dumps(response).encode('utf-8'))
        sock.close()
        delattr(self, 'pending_invitation')
        return True
    
    def _perform_key_exchange(self, initiator: bool) -> bool:
        """
        Perform Diffie-Hellman key exchange.
        
        Args:
            initiator: True if this peer initiated the connection
            
        Returns:
            True on success
        """
        try:
            # Generate DH keypair
            dh_public_key = self.crypto.generate_dh_keypair()
            
            # Sign DH public key
            signature = self.crypto.sign_data(dh_public_key)
            
            # Prepare key exchange message
            key_exchange = {
                'type': 'key_exchange',
                'dh_public_key': dh_public_key.decode('utf-8'),
                'signature': signature.hex()
            }
            
            if initiator:
                # Send our DH public key
                if not self.network.send_message(
                    self.peer_socket,
                    json.dumps(key_exchange).encode('utf-8')
                ):
                    return False
                
                # Receive peer's DH public key
                response_data = self.network.receive_message(self.peer_socket, timeout=10.0)
                if not response_data:
                    return False
            else:
                # Receive peer's DH public key first
                peer_key_data = self.network.receive_message(self.peer_socket, timeout=10.0)
                if not peer_key_data:
                    return False
                
                # Send our DH public key
                if not self.network.send_message(
                    self.peer_socket,
                    json.dumps(key_exchange).encode('utf-8')
                ):
                    return False
                
                response_data = peer_key_data
            
            # Parse peer's key exchange
            peer_exchange = json.loads(response_data.decode('utf-8'))
            peer_dh_public_key = peer_exchange['dh_public_key'].encode('utf-8')
            peer_signature = bytes.fromhex(peer_exchange['signature'])
            
            # Verify peer's signature
            peer_public_key = serialization.load_pem_public_key(
                self.peer_public_key,
                backend=default_backend()
            )
            
            if not self.crypto.verify_signature(peer_dh_public_key, peer_signature, peer_public_key):
                print("Failed to verify peer's DH key signature")
                return False
            
            # Compute shared secret
            self.crypto.compute_shared_secret(peer_dh_public_key)
            
            # Update session state
            self.session.state = SessionState.CONNECTED
            self.session.established_at = time.time()
            self.session.last_activity = time.time()
            self.session.key_rotation_at = time.time() + self.TIME_BEFORE_REKEY
            self._update_state(SessionState.CONNECTED)
            
            # Start receive thread
            self.running = True
            self.receive_counter = 0
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            
            return True
        except Exception as e:
            import traceback
            print(f"Error in key exchange: {e}")
            print(f"Traceback: {traceback.format_exc()}")  # Show full error for debugging
            return False
    
    def send_message(self, message: str) -> bool:
        """
        Send encrypted message to peer.
        
        Args:
            message: Plain text message
            
        Returns:
            True on success
        """
        if not self.session or self.session.state != SessionState.CONNECTED:
            return False
        
        try:
            # Encrypt message
            encrypted = self.crypto.encrypt_message(message)
            
            # Prepare message packet
            packet = {
                'type': 'message',
                'data': encrypted.hex()
            }
            
            # Send
            if not self.network.send_message(
                self.peer_socket,
                json.dumps(packet).encode('utf-8')
            ):
                return False
            
            # Update session
            self.session.messages_sent += 1
            self.session.last_activity = time.time()
            
            # Check if rekey needed
            if (self.session.messages_sent >= self.MESSAGES_BEFORE_REKEY or
                time.time() >= self.session.key_rotation_at):
                threading.Thread(target=self._perform_rekey, daemon=True).start()
            
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def _receive_messages(self):
        """Receive and decrypt messages from peer."""
        while self.running and self.peer_socket:
            try:
                data = self.network.receive_message(self.peer_socket, timeout=1.0)
                if not data:
                    continue
                
                packet = json.loads(data.decode('utf-8'))
                
                if packet['type'] == 'message':
                    # Decrypt message
                    encrypted = bytes.fromhex(packet['data'])
                    plaintext, counter = self.crypto.decrypt_message(encrypted, self.receive_counter)
                    
                    # Update counter
                    self.receive_counter = counter + 1
                    
                    # Update session
                    self.session.last_activity = time.time()
                    
                    # Callback
                    if self.on_message_received:
                        self.on_message_received(plaintext)
                
                elif packet['type'] == 'rekey_request':
                    self._handle_rekey_request()
                
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}")
    
    def _perform_rekey(self):
        """Perform session key rotation."""
        # Try to acquire the lock, return if already in progress
        if not self.rekey_lock.acquire(blocking=False):
            return  # Rekey already in progress
        
        try:
            if not self.session or self.session.state != SessionState.CONNECTED:
                return
            
            # Send rekey request
            request = {'type': 'rekey_request'}
            self.network.send_message(
                self.peer_socket,
                json.dumps(request).encode('utf-8')
            )
            
            # Reset crypto state
            self.crypto.reset_session_key()
            
            # Perform new key exchange
            self._perform_key_exchange(initiator=True)
        except Exception as e:
            print(f"Error during rekey: {e}")
        finally:
            self.rekey_lock.release()
    
    def _handle_rekey_request(self):
        """Handle incoming rekey request."""
        # Reset crypto state
        self.crypto.reset_session_key()
        
        # Perform new key exchange
        self._perform_key_exchange(initiator=False)
    
    def request_key_rotation(self):
        """
        Public method to request key rotation.
        This should be used instead of calling _perform_rekey directly.
        """
        if self.session and self.session.state == SessionState.CONNECTED:
            threading.Thread(target=self._perform_rekey, daemon=True).start()
    
    def disconnect(self):
        """Disconnect from current session."""
        self.running = False
        
        if self.peer_socket:
            try:
                # Send disconnect message
                disconnect_msg = {'type': 'disconnect'}
                self.network.send_message(
                    self.peer_socket,
                    json.dumps(disconnect_msg).encode('utf-8')
                )
                self.peer_socket.close()
            except:
                pass
            self.peer_socket = None
        
        # Clear session
        self.session = None
        self.peer_public_key = None
        self.crypto.reset_session_key()
        self._update_state(SessionState.DISCONNECTED)
    
    def _update_state(self, state: SessionState):
        """Update session state and notify callback."""
        if self.session:
            self.session.state = state
        if self.on_state_changed:
            self.on_state_changed(state)
    
    def get_status(self) -> dict:
        """Get current session status."""
        if not self.session:
            return {'state': 'disconnected'}
        
        return {
            'state': self.session.state.value,
            'peer_id': self.session.peer_id,
            'peer_address': self.session.peer_address,
            'established_at': self.session.established_at,
            'messages_sent': self.session.messages_sent,
            'session_key_active': self.crypto.session_key is not None
        }
