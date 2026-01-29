#!/usr/bin/env python3
"""
Demo script showing the Secure Terminal Chat application interface.
This script demonstrates the UI without requiring actual network connections.
"""

import time
from secure_chat.ui import ChatUI


def demo_ui():
    """Demonstrate the chat UI."""
    ui = ChatUI()
    
    # Show welcome info (without requiring input)
    print("\n" + "="*70)
    print("DEMO: Welcome Screen")
    print("="*70)
    
    ui.console.print("""
[bold cyan]╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🔒 SECURE TERMINAL CHAT APPLICATION 🔒            ║
║                                                           ║
║            End-to-End Encrypted Chat System              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝[/bold cyan]

[yellow]Features:[/yellow]
  • End-to-End Encryption (AES-256-GCM)
  • Authenticated Key Exchange (DH + RSA)
  • Perfect Forward Secrecy
  • Replay Attack Protection
""")
    
    ui.start()
    
    # Simulate some messages
    print("\n" + "="*70)
    print("DEMO: Chat Messages")
    print("="*70)
    
    ui.add_system_message("Your Peer ID: peer_demo123", "cyan")
    ui.add_system_message("Listening on port: 50001", "cyan")
    ui.add_system_message("Type /help for available commands", "yellow")
    ui.add_system_message("")
    
    # Simulate peer discovery
    time.sleep(1)
    ui.add_system_message("Scanning for peers on the network...", "yellow")
    
    # Show discovered peers (simulated)
    from secure_chat.core import PeerInfo
    peers = [
        PeerInfo("peer_abc123", "192.168.1.100", 50001, b"dummy_key"),
        PeerInfo("peer_xyz789", "192.168.1.101", 50002, b"dummy_key"),
    ]
    
    print("\n" + "="*70)
    print("DEMO: Discovered Peers")
    print("="*70)
    ui.show_peers(peers)
    
    # Show connection progress
    time.sleep(1)
    print("\n" + "="*70)
    print("DEMO: Connection Process")
    print("="*70)
    ui.add_system_message("Sending invitation to peer_abc123...", "yellow")
    time.sleep(0.5)
    ui.add_system_message("Key exchange in progress...", "yellow")
    time.sleep(0.5)
    ui.add_system_message("✓ Connected and encrypted", "green")
    
    # Show chat messages
    print("\n" + "="*70)
    print("DEMO: Chat Conversation")
    print("="*70)
    ui.add_message("You", "Hello! This is a secure message.")
    time.sleep(0.3)
    ui.add_message("peer_abc123", "Hi! I received your encrypted message.")
    time.sleep(0.3)
    ui.add_message("You", "Great! All our messages are encrypted with AES-256-GCM.")
    time.sleep(0.3)
    ui.add_message("peer_abc123", "Perfect forward secrecy with automatic key rotation!")
    
    # Show invitation
    print("\n" + "="*70)
    print("DEMO: Incoming Invitation")
    print("="*70)
    ui.show_invitation("peer_xyz789", "192.168.1.101")
    
    # Show status
    print("\n" + "="*70)
    print("DEMO: Security Status")
    print("="*70)
    status = {
        'state': 'connected',
        'peer_id': 'peer_abc123',
        'peer_address': '192.168.1.100',
        'established_at': time.time() - 300,  # 5 minutes ago
        'messages_sent': 42,
        'session_key_active': True
    }
    ui.show_status(status)
    
    # Show help (without requiring input)
    print("\n" + "="*70)
    print("DEMO: Help Screen (Sample)")
    print("="*70)
    
    ui.console.print("""
[bold cyan]═══════════════════════════════════════════════════════════
                    COMMAND REFERENCE
═══════════════════════════════════════════════════════════[/bold cyan]

[yellow]Network Commands:[/yellow]
  [bold]/discover[/bold]      - Scan for peers on the local network
  [bold]/connect <#>[/bold]   - Send connection invitation to peer

[yellow]Connection Commands:[/yellow]
  [bold]/accept[/bold]        - Accept incoming connection invitation
  [bold]/disconnect[/bold]    - End current chat session

[yellow]Security Commands:[/yellow]
  [bold]/rekey[/bold]         - Force session key rotation
  [bold]/status[/bold]        - Show detailed security status
""")
    
    # Show error and success examples
    print("\n" + "="*70)
    print("DEMO: Error and Success Messages")
    print("="*70)
    ui.show_error("Connection failed - peer not responding")
    time.sleep(0.5)
    ui.show_success("Session key rotated successfully")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         SECURE TERMINAL CHAT - UI DEMONSTRATION                 ║
║                                                                  ║
║  This demo shows the various UI screens and features            ║
║  without requiring actual network connections.                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    demo_ui()
