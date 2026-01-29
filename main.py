#!/usr/bin/env python3
"""
Main entry point for Secure Terminal Chat Application.

This application provides end-to-end encrypted peer-to-peer chat
over local networks with secure key exchange and authentication.
"""

import sys
import socket
import uuid
from typing import Optional

from secure_chat.core import (
    CryptoManager,
    KeyManager,
    NetworkManager,
    PeerInfo,
    SessionManager,
    SessionState,
)
from secure_chat.ui import ChatUI
from secure_chat.utils import SecurityLogger


class SecureChatApp:
    """Main application class for Secure Terminal Chat."""
    
    def __init__(self):
        """Initialize the chat application."""
        # Generate unique peer ID
        self.peer_id = f"peer_{uuid.uuid4().hex[:8]}"
        
        # Initialize managers
        self.key_manager = KeyManager()
        self.crypto = CryptoManager()
        self.network = NetworkManager(self.peer_id)
        self.session: Optional[SessionManager] = None
        self.ui = ChatUI()
        self.logger = SecurityLogger(self.key_manager.get_log_file_path())
        
        # Discovered peers
        self.discovered_peers = []
        
        # State
        self.running = False
        
    def initialize_keys(self):
        """Initialize or load RSA keys."""
        if self.key_manager.keys_exist():
            # Load existing keys
            private_pem, public_pem = self.key_manager.load_keys()
            self.crypto.load_rsa_private_key(private_pem)
            self.logger.log_key_loaded()
            self.ui.add_system_message("Loaded existing RSA keys")
        else:
            # Generate new keys
            self.ui.add_system_message("Generating RSA key pair (this may take a moment)...")
            private_pem, public_pem = self.crypto.generate_rsa_keypair()
            self.key_manager.save_keys(private_pem, public_pem)
            self.logger.log_key_generation()
            self.ui.add_system_message("Generated and saved new RSA keys", "green")
    
    def start(self):
        """Start the chat application."""
        try:
            # Show welcome screen
            self.ui.show_welcome()
            self.ui.start()
            
            # Initialize keys
            self.initialize_keys()
            
            # Start network services
            tcp_port = self.network.start_tcp_server()
            public_key = self.key_manager.get_public_key()
            self.network.start_discovery_responder(public_key)
            
            # Set up network callbacks
            self.network.on_connection_received = self.handle_incoming_connection
            
            # Initialize session manager
            self.session = SessionManager(self.crypto, self.network)
            self.session.on_message_received = self.handle_message_received
            self.session.on_state_changed = self.handle_state_changed
            self.session.on_invitation_received = self.handle_invitation_received
            
            # Show info
            self.ui.add_system_message(f"Your Peer ID: {self.peer_id}", "cyan")
            self.ui.add_system_message(f"Listening on port: {tcp_port}", "cyan")
            self.ui.add_system_message("Type /help for available commands", "yellow")
            self.ui.add_system_message("")
            
            # Main loop
            self.running = True
            self.main_loop()
            
        except KeyboardInterrupt:
            self.ui.add_system_message("\nShutting down...", "yellow")
        except Exception as e:
            self.ui.show_error(f"Fatal error: {e}")
        finally:
            self.shutdown()
    
    def main_loop(self):
        """Main application loop."""
        while self.running:
            try:
                # Get user input
                user_input = self.ui.prompt_input()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                else:
                    # Send message
                    if self.session and self.session.session:
                        if self.session.session.state == SessionState.CONNECTED:
                            if self.session.send_message(user_input):
                                self.ui.add_message("You", user_input)
                                self.logger.log_message_sent(self.session.session.peer_id)
                            else:
                                self.ui.show_error("Failed to send message")
                        else:
                            self.ui.show_error("Not connected to a peer")
                    else:
                        self.ui.show_error("Not connected to a peer. Use /discover and /connect")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.ui.show_error(f"Error: {e}")
    
    def handle_command(self, command: str):
        """
        Handle user commands.
        
        Args:
            command: Command string
        """
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == '/quit':
            self.running = False
            
        elif cmd == '/help':
            self.ui.show_help()
            
        elif cmd == '/discover':
            self.discover_peers()
            
        elif cmd == '/connect':
            if not args:
                self.ui.show_error("Usage: /connect <peer_number>")
            else:
                try:
                    peer_num = int(args)
                    self.connect_to_peer(peer_num)
                except ValueError:
                    self.ui.show_error("Invalid peer number")
                    
        elif cmd == '/accept':
            self.accept_invitation()
            
        elif cmd == '/reject':
            self.reject_invitation()
            
        elif cmd == '/disconnect':
            self.disconnect()
            
        elif cmd == '/rekey':
            self.rekey()
            
        elif cmd == '/status':
            self.show_status()
            
        else:
            self.ui.show_error(f"Unknown command: {cmd}. Type /help for available commands")
    
    def discover_peers(self):
        """Discover peers on the network."""
        self.ui.add_system_message("Scanning for peers on the network...", "yellow")
        
        peers = self.network.discover_peers(timeout=2.0)
        self.discovered_peers = peers
        
        for peer in peers:
            self.logger.log_peer_discovered(peer.peer_id, peer.address)
        
        self.ui.show_peers(peers)
    
    def connect_to_peer(self, peer_num: int):
        """
        Connect to a discovered peer.
        
        Args:
            peer_num: Peer number from discovery list
        """
        if not self.discovered_peers:
            self.ui.show_error("No peers discovered. Use /discover first")
            return
        
        if peer_num < 1 or peer_num > len(self.discovered_peers):
            self.ui.show_error(f"Invalid peer number. Choose 1-{len(self.discovered_peers)}")
            return
        
        peer = self.discovered_peers[peer_num - 1]
        
        self.ui.add_system_message(f"Sending invitation to {peer.peer_id}...", "yellow")
        self.logger.log_invitation_sent(peer.peer_id, peer.address)
        
        if self.session.send_invitation(peer):
            self.ui.show_success(f"Connected to {peer.peer_id}")
            self.logger.log_connection_established(peer.peer_id, peer.address)
        else:
            self.ui.show_error("Failed to connect")
            self.logger.log_connection_failed(peer.peer_id, "invitation_failed")
    
    def handle_incoming_connection(self, sock: socket.socket, address: str):
        """
        Handle incoming connection.
        
        Args:
            sock: Client socket
            address: Client address
        """
        try:
            # Receive first message (should be invitation)
            data = self.network.receive_message(sock, timeout=5.0)
            if data:
                self.session.handle_invitation(sock, data)
        except Exception as e:
            self.ui.show_error(f"Error handling incoming connection: {e}")
    
    def handle_invitation_received(self, peer_id: str, address: str):
        """
        Handle incoming invitation notification.
        
        Args:
            peer_id: Peer ID
            address: Peer address
        """
        self.logger.log_invitation_received(peer_id, address)
        self.ui.show_invitation(peer_id, address)
    
    def accept_invitation(self):
        """Accept pending invitation."""
        if self.session.accept_invitation():
            self.ui.show_success("Invitation accepted. Key exchange in progress...")
            if hasattr(self.session, 'pending_invitation'):
                self.logger.log_invitation_accepted(
                    self.session.pending_invitation['peer_id']
                )
        else:
            self.ui.show_error("No pending invitation")
    
    def reject_invitation(self):
        """Reject pending invitation."""
        if self.session.reject_invitation():
            self.ui.add_system_message("Invitation rejected", "yellow")
            if hasattr(self.session, 'pending_invitation'):
                self.logger.log_invitation_rejected(
                    self.session.pending_invitation['peer_id']
                )
        else:
            self.ui.show_error("No pending invitation")
    
    def disconnect(self):
        """Disconnect from current session."""
        if self.session and self.session.session:
            peer_id = self.session.session.peer_id
            self.session.disconnect()
            self.ui.add_system_message("Disconnected", "yellow")
            self.logger.log_disconnection(peer_id)
        else:
            self.ui.show_error("Not connected")
    
    def rekey(self):
        """Force session key rotation."""
        if self.session and self.session.session:
            if self.session.session.state == SessionState.CONNECTED:
                self.ui.add_system_message("Initiating key rotation...", "yellow")
                self.session.request_key_rotation()
                self.logger.log_key_rotation(self.session.session.peer_id)
            else:
                self.ui.show_error("Not in connected state")
        else:
            self.ui.show_error("Not connected")
    
    def show_status(self):
        """Show current status."""
        if self.session:
            status = self.session.get_status()
            self.ui.show_status(status)
        else:
            self.ui.show_status({'state': 'disconnected'})
    
    def handle_message_received(self, message: str):
        """
        Handle received message.
        
        Args:
            message: Decrypted message text
        """
        if self.session and self.session.session:
            self.ui.add_message(self.session.session.peer_id, message)
            self.logger.log_message_received(self.session.session.peer_id)
    
    def handle_state_changed(self, state: SessionState):
        """
        Handle session state change.
        
        Args:
            state: New session state
        """
        state_messages = {
            SessionState.DISCONNECTED: ("Disconnected", "yellow"),
            SessionState.INVITATION_SENT: ("Invitation sent", "yellow"),
            SessionState.INVITATION_RECEIVED: ("Invitation received", "yellow"),
            SessionState.KEY_EXCHANGE: ("Key exchange in progress...", "yellow"),
            SessionState.CONNECTED: ("✓ Connected and encrypted", "green"),
            SessionState.ERROR: ("Connection error", "red"),
        }
        
        if state in state_messages:
            msg, style = state_messages[state]
            self.ui.add_system_message(msg, style)
            
            if state == SessionState.CONNECTED and self.session and self.session.session:
                self.logger.log_key_exchange_completed(self.session.session.peer_id)
    
    def shutdown(self):
        """Shutdown the application."""
        if self.session:
            self.session.disconnect()
        
        if self.network:
            self.network.stop()
        
        self.ui.stop()
        sys.exit(0)


def main():
    """Main entry point."""
    app = SecureChatApp()
    app.start()


if __name__ == '__main__':
    main()
