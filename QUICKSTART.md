# Quick Start Guide

## Installation

### Option 1: Using pip (Recommended)
```bash
# Clone the repository
git clone https://github.com/YashasJKumar/Secure-Terminal-Chat.git
cd Secure-Terminal-Chat

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 2: Using setup.py
```bash
# Clone the repository
git clone https://github.com/YashasJKumar/Secure-Terminal-Chat.git
cd Secure-Terminal-Chat

# Install the package
pip install -e .

# Run the application
python main.py
```

## First Time Setup

When you run the application for the first time:

1. **Key Generation**: The application automatically generates RSA-2048 key pairs
   - Keys are stored in `~/.secure_chat/keys/`
   - Private key has restricted permissions (0600)
   - This only happens once

2. **Network Setup**: The application starts:
   - TCP server for incoming connections (random port)
   - UDP responder for peer discovery (port 50000)
   - Your unique Peer ID is displayed

## Basic Usage

### 1. Discover Peers

```
> /discover
```

This command:
- Broadcasts UDP discovery message on the local network
- Displays a numbered list of discovered peers
- Shows peer IDs, IP addresses, and ports

Example output:
```
📡 Discovered Peers
#  Peer ID      IP Address     Port
1  peer_abc123  192.168.1.100  50001
2  peer_xyz789  192.168.1.101  50002
```

### 2. Connect to a Peer

```
> /connect 1
```

This initiates:
1. Sends connection invitation to peer #1
2. Peer must accept the invitation
3. Authenticated key exchange (DH + RSA signatures)
4. Session key derivation (AES-256)
5. Connection established

### 3. Accept/Reject Invitations

When you receive an invitation:

```
📨 Incoming Connection Invitation
Peer ID: peer_xyz789
Address: 192.168.1.101

Use /accept to accept or /reject to reject
```

To accept:
```
> /accept
```

To reject:
```
> /reject
```

### 4. Send Messages

Once connected, simply type your message:

```
> Hello! This is a secure message.
```

All messages are automatically:
- Encrypted with AES-256-GCM
- Authenticated with GCM tag
- Protected against replay attacks
- Timestamped

### 5. Check Security Status

```
> /status
```

Shows:
- Connection state
- Peer information
- Encryption status
- Session duration
- Messages sent

### 6. Force Key Rotation

```
> /rekey
```

Manually triggers:
- New Diffie-Hellman exchange
- New session key derivation
- Message counter reset

Note: Keys automatically rotate every:
- 100 messages, OR
- 30 minutes (whichever comes first)

### 7. Disconnect

```
> /disconnect
```

This:
- Sends disconnect notification to peer
- Closes TCP connection
- Clears session keys from memory
- Returns to discovery mode

### 8. Exit Application

```
> /quit
```

Cleanly exits the application:
- Disconnects active sessions
- Closes network sockets
- Clears sensitive data from memory

## Two-Device Example Session

### Device A (192.168.1.100)
```bash
$ python main.py

Your Peer ID: peer_abc123
Listening on port: 50001

> /discover
📡 Discovered Peers
#  Peer ID      IP Address     Port
1  peer_xyz789  192.168.1.101  50002

> /connect 1
System: Sending invitation to peer_xyz789...
System: Key exchange in progress...
System: ✓ Connected and encrypted

> Hello from Device A!
You: Hello from Device A!
peer_xyz789: Hello from Device B!
```

### Device B (192.168.1.101)
```bash
$ python main.py

Your Peer ID: peer_xyz789
Listening on port: 50002

📨 Incoming Connection Invitation
Peer ID: peer_abc123
Address: 192.168.1.100

> /accept
System: Invitation accepted. Key exchange in progress...
System: ✓ Connected and encrypted

peer_abc123: Hello from Device A!
> Hello from Device B!
You: Hello from Device B!
```

## Testing on Single Machine

You can test on one machine by:

1. Open two terminal windows
2. Run `python main.py` in each
3. Each instance gets a unique Peer ID
4. Use `/discover` in both terminals
5. Connect from one to the other

Example:
```bash
# Terminal 1
$ python main.py
Your Peer ID: peer_abc123
> /discover
> /connect 1

# Terminal 2
$ python main.py
Your Peer ID: peer_xyz789
> /accept
```

## Command Reference

| Command | Description |
|---------|-------------|
| `/discover` | Scan for peers on local network |
| `/connect <#>` | Send invitation to peer number |
| `/accept` | Accept incoming invitation |
| `/reject` | Reject incoming invitation |
| `/disconnect` | End current session |
| `/rekey` | Force session key rotation |
| `/status` | Show detailed security status |
| `/help` | Show help information |
| `/quit` | Exit application |

## Security Features in Action

### 1. Replay Attack Prevention

The application rejects:
- Messages with old timestamps (>60 seconds)
- Messages with old sequence numbers

You'll see:
```
Error: Message timestamp too old - possible replay attack
```

### 2. Signature Verification

During key exchange, if signatures don't verify:
```
Error: Failed to verify peer's DH key signature
```

### 3. Encryption Status

Check if encryption is active:
```
> /status

🔐 Security Status
Connection State: connected
Peer ID: peer_abc123
Encryption: ✓ Active (AES-256-GCM)
```

### 4. Automatic Key Rotation

The system automatically notifies:
```
System: Initiating key rotation...
System: ✓ Key rotation complete
```

## Troubleshooting

### No peers discovered
- Check firewall settings (allow UDP port 50000)
- Ensure devices are on same local network
- Try running with sudo/admin rights

### Connection failed
- Verify peer is running and accepting connections
- Check firewall for TCP connections
- Ensure stable network connection

### Decryption failed
- May indicate network corruption
- Possible replay attack detected
- Solution: Disconnect and reconnect

### Permission errors
- Ensure write access to home directory
- Check `~/.secure_chat/` directory permissions
- Key files need proper permissions (0600)

## Files and Directories

```
~/.secure_chat/
├── keys/
│   ├── private_key.pem    # RSA private key (0600)
│   └── public_key.pem     # RSA public key (0644)
├── logs/
│   └── security.log       # Security audit trail
└── config.json            # Optional configuration
```

## Security Best Practices

1. **Protect Your Keys**
   - Never share `private_key.pem`
   - Back up keys securely if needed
   - Regenerate keys if compromised

2. **Network Security**
   - Use on trusted networks only
   - Be cautious on public WiFi
   - Verify peer identities

3. **Session Management**
   - Use `/status` to verify encryption
   - Use `/rekey` if session is suspicious
   - Disconnect when done

4. **Audit Logs**
   - Check `~/.secure_chat/logs/security.log`
   - Review for unusual activity
   - Logs don't contain message content

## Configuration (Optional)

Create `~/.secure_chat/config.json`:

```json
{
  "tcp_port": 0,
  "discovery_timeout": 2.0,
  "session_timeout": 1800,
  "rekey_message_count": 100,
  "rekey_time_seconds": 1800
}
```

## Getting Help

For issues or questions:
- Run `/help` in the application
- Check the main README.md
- Review security logs
- Open an issue on GitHub

## Running Tests

Test cryptographic operations:
```bash
python test_crypto.py
```

Expected output:
```
============================================================
SECURE CHAT CRYPTOGRAPHY TESTS
============================================================

✓ Digital signature successful
✓ Diffie-Hellman key exchange successful
✓ Message encryption/decryption successful
✓ Replay attack correctly detected
✓ HMAC computation and verification successful

============================================================
✓ ALL TESTS PASSED
============================================================
```
