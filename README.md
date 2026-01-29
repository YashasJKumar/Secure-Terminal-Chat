# 🔒 Secure Terminal Chat

A secure, end-to-end encrypted terminal-based chat application for peer-to-peer communication over local networks. Built with Python, featuring real-world cryptographic protocols including authenticated key exchange, message encryption, and protection against common attacks.

## ✨ Features

### Security Features
- **End-to-End Encryption**: AES-256-GCM for message encryption with built-in authentication
- **Authenticated Key Exchange**: Diffie-Hellman key exchange with RSA signatures
- **Perfect Forward Secrecy**: Automatic session key rotation every 100 messages or 30 minutes
- **Replay Attack Protection**: Timestamp verification and message sequence numbers
- **Man-in-the-Middle Protection**: RSA signatures verify key exchange authenticity
- **Secure Key Storage**: RSA keys stored with restricted permissions in `~/.secure_chat/`

### Network Features
- **Peer Discovery**: Automatic discovery of peers on local network via UDP broadcast
- **Invitation-Based Connections**: Explicit invitation/acceptance mechanism
- **TCP Socket Communication**: Reliable peer-to-peer messaging
- **Session Management**: Automatic timeout and graceful disconnection

### User Interface
- **Rich Terminal UI**: Clean, intuitive interface using the Rich library
- **Real-time Messaging**: Instant message display with timestamps
- **System Notifications**: Clear feedback on connection status and security events
- **Command-Based Interface**: Simple commands for all operations

## 🏗️ Architecture

### Cryptographic Protocol

#### 1. Initial Setup (First Launch)
```
┌─────────────────────────────────────┐
│ Generate RSA-2048 Key Pair          │
│ Save to ~/.secure_chat/keys/        │
└─────────────────────────────────────┘
```

#### 2. Peer Discovery
```
Peer A                                    Peer B
   │                                         │
   ├──[UDP Broadcast: DISCOVERY]────────────>│
   │                                         │
   │<─[UDP Response: ID, Port, Public Key]──┤
   │                                         │
```

#### 3. Connection Establishment
```
Peer A                                    Peer B
   │                                         │
   ├──[TCP: Invitation + RSA Signature]────>│
   │                                         │
   │<─────[Accept/Reject]────────────────────┤
   │                                         │
```

#### 4. Authenticated Key Exchange
```
Peer A                                    Peer B
   │                                         │
   ├─[DH Public Key + RSA Signature]───────>│
   │                                         │
   │<──[DH Public Key + RSA Signature]──────┤
   │                                         │
   ├─[Verify Signature]                     │
   │                    [Verify Signature]──┤
   │                                         │
   ├─[Compute Shared Secret]                │
   │                [Compute Shared Secret]─┤
   │                                         │
   ├─[Derive AES-256 Key via PBKDF2]        │
   │            [Derive AES-256 Key]────────┤
   │                                         │
```

#### 5. Encrypted Communication
```
┌──────────────────────────────────────────────┐
│ Message Format:                              │
│ [IV(12)] [Ciphertext] [Auth Tag(16)]        │
│ [Timestamp(8)] [Counter(4)]                 │
│                                              │
│ Encryption: AES-256-GCM                     │
│ Additional Data: Timestamp + Counter        │
└──────────────────────────────────────────────┘
```

### Module Structure

```
secure_chat/
├── core/
│   ├── crypto.py          # Cryptographic operations (RSA, DH, AES-GCM)
│   ├── key_manager.py     # Key storage and loading
│   ├── network.py         # TCP/UDP networking
│   └── session.py         # Session management and protocols
├── ui/
│   └── terminal.py        # Rich-based terminal interface
└── utils/
    └── logger.py          # Security event logging
```

## 📋 Requirements

- Python 3.8 or higher
- Linux, macOS, or Windows
- Local network connectivity for peer discovery

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YashasJKumar/Secure-Terminal-Chat.git
cd Secure-Terminal-Chat
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Or install dependencies individually:
```bash
pip install cryptography rich
```

### 3. Run the Application
```bash
python main.py
```

## 📖 Usage Guide

### Starting the Application

When you first launch the application:
1. Welcome screen displays features and commands
2. RSA keys are generated (first launch) or loaded (subsequent launches)
3. Network services start automatically
4. Your unique Peer ID is displayed

### Available Commands

#### Network Discovery
```
/discover
```
Scans the local network for other peers running the application. Displays a numbered list of discovered peers with their IDs, IP addresses, and ports.

#### Connecting to a Peer
```
/connect <peer_number>
```
Sends a connection invitation to the specified peer. The peer must accept the invitation before communication begins.

Example:
```
/connect 1    # Connect to peer #1 from the discovery list
```

#### Accepting/Rejecting Invitations
```
/accept       # Accept incoming invitation
/reject       # Reject incoming invitation
```
When another peer sends you an invitation, you'll see a notification. Use these commands to respond.

#### Sending Messages
Once connected, simply type your message and press Enter. All messages are automatically encrypted before transmission.

```
Hello, this is a secure message!
```

#### Session Management
```
/disconnect   # End current session
/rekey        # Force session key rotation
/status       # Show detailed security status
```

#### Other Commands
```
/help         # Show command reference
/quit         # Exit application
```

### Example Session

```
# Terminal 1 (Peer A)
> /discover
📡 Discovered Peers
#  Peer ID      IP Address     Port
1  peer_abc123  192.168.1.100  50001

> /connect 1
System: Sending invitation to peer_abc123...
System: Key exchange in progress...
System: ✓ Connected and encrypted
You: Hello from Peer A!
peer_abc123: Hello from Peer B!

# Terminal 2 (Peer B)
📨 Incoming Connection Invitation
Peer ID: peer_xyz789
Address: 192.168.1.101

> /accept
System: Invitation accepted. Key exchange in progress...
System: ✓ Connected and encrypted
peer_xyz789: Hello from Peer A!
You: Hello from Peer B!
```

## 🔐 Security Architecture

### Threat Model

This application protects against:

1. **Eavesdropping**: All messages encrypted with AES-256-GCM
2. **Man-in-the-Middle Attacks**: RSA signatures authenticate key exchange
3. **Replay Attacks**: Timestamp validation and sequence numbers
4. **Message Tampering**: GCM authentication tags verify integrity
5. **Forward Secrecy Loss**: Automatic key rotation protects past messages

### Cryptographic Components

#### RSA (2048-bit)
- **Purpose**: Authentication and digital signatures
- **Usage**: Sign DH public keys during key exchange
- **Key Storage**: PEM format in `~/.secure_chat/keys/` with 0600 permissions

#### Diffie-Hellman (2048-bit)
- **Purpose**: Session key establishment
- **Usage**: Generate shared secret for AES key derivation
- **Parameters**: RFC 3526 Group 14 (standardized 2048-bit MODP Group)
- **Note**: All peers use the same standardized parameters to ensure compatibility

#### AES-256-GCM
- **Purpose**: Message encryption and authentication
- **Key Derivation**: PBKDF2-HMAC-SHA256 from DH shared secret
- **IV**: 12 bytes, randomly generated per message
- **Authentication**: 16-byte tag, covers ciphertext + metadata

#### HMAC-SHA256
- **Purpose**: Control message authentication
- **Usage**: Additional protection for critical protocol messages

### Key Rotation

Session keys automatically rotate when:
- 100 messages have been sent in the current session, OR
- 30 minutes have elapsed since key establishment

Rotation process:
1. Peer A sends rekey request
2. Both peers reset cryptographic state
3. New Diffie-Hellman exchange performed
4. New session key derived
5. Message counters reset
6. Old keys securely deleted from memory

### Security Logging

All security events are logged to `~/.secure_chat/logs/security.log`:
- Key generation and loading
- Peer discovery
- Connection attempts (success/failure)
- Key exchange events
- Authentication failures
- Detected attacks
- Session lifecycle events

**Note**: Message content is NEVER logged to preserve privacy.

## 🗂️ File Structure

```
~/.secure_chat/
├── keys/
│   ├── private_key.pem    # RSA private key (0600 permissions)
│   └── public_key.pem     # RSA public key
├── logs/
│   └── security.log       # Security event audit trail
└── config.json            # Application configuration (optional)
```

## 🔧 Configuration

The application uses secure defaults. Optional configuration can be stored in `~/.secure_chat/config.json`:

```json
{
  "tcp_port": 0,              
  "discovery_timeout": 2.0,   
  "session_timeout": 1800,    
  "rekey_message_count": 100, 
  "rekey_time_seconds": 1800  
}
```

## 🐛 Troubleshooting

### No Peers Discovered
- **Cause**: Firewall blocking UDP port 50000
- **Solution**: Allow UDP broadcast on port 50000
- **Check**: Ensure both peers are on the same local network

### Connection Failed
- **Cause**: Firewall blocking TCP connections
- **Solution**: Allow incoming TCP connections on the ephemeral port range
- **Note**: Application uses random TCP ports for peer connections

### Key Exchange Failed
- **Cause**: Network interruption during handshake
- **Solution**: Retry connection after ensuring stable network

### Decryption Failed
- **Possible Causes**:
  - Network packet corruption
  - Replay attack detected (old message)
  - Session keys out of sync
- **Solution**: Disconnect and reconnect to establish new session

### Permission Errors
- **Cause**: Cannot create `~/.secure_chat/` directory
- **Solution**: Ensure write permissions in home directory

## 🧪 Testing

### Testing Locally

You can test the application on a single machine:

1. Open two terminal windows
2. Run `python main.py` in each terminal
3. Each instance will have a unique Peer ID
4. Use `/discover` in both terminals
5. Connect from one terminal to the other

### Testing on Network

1. Install application on two or more devices
2. Ensure devices are on the same local network
3. Run application on each device
4. Use `/discover` to find peers
5. Establish connections and test messaging

## 🔒 Security Considerations

### What This Application Provides
✅ End-to-end encryption for message content  
✅ Authentication of communication parties  
✅ Protection against passive eavesdropping  
✅ Protection against active MITM attacks (via signatures)  
✅ Perfect forward secrecy through key rotation  
✅ Replay attack protection  

### What This Application Does NOT Provide
❌ Anonymity or IP address hiding  
❌ Protection against compromised endpoints  
❌ Secure group chat (only peer-to-peer)  
❌ Long-term message storage or history  
❌ Identity verification beyond cryptographic keys  

### Best Practices
1. **Key Security**: Protect your `~/.secure_chat/keys/` directory
2. **Physical Security**: Ensure your device is secure
3. **Network Trust**: Use on trusted local networks only
4. **Regular Updates**: Keep dependencies updated for security patches
5. **Key Rotation**: Use `/rekey` if you suspect session compromise

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional encryption algorithms
- Group chat support
- GUI interface
- Mobile app versions
- Enhanced peer verification (QR codes, fingerprints)

## 📧 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review security logs in `~/.secure_chat/logs/`

## 🙏 Acknowledgments

Built with:
- [cryptography](https://cryptography.io/) - Cryptographic primitives
- [Rich](https://rich.readthedocs.io/) - Terminal UI framework

---

**⚠️ Educational Use**: This application demonstrates cryptographic protocols and secure communication. While it implements real security measures, it has not undergone professional security audit. Use in production environments at your own risk.
