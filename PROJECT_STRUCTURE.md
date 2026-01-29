# Project Structure

This document describes the structure and purpose of all files in the Secure Terminal Chat project.

## Root Directory

### Main Application
- **`main.py`** - Main entry point for the application. Initializes all components and runs the main event loop.

### Configuration & Setup
- **`setup.py`** - Python package setup configuration for pip installation
- **`requirements.txt`** - Python dependencies (cryptography, rich)
- **`config.example.json`** - Example configuration file with default settings

### Documentation
- **`README.md`** - Main project documentation with architecture, features, and usage
- **`QUICKSTART.md`** - Quick start guide for users to get up and running
- **`SECURITY.md`** - Comprehensive security analysis and assessment

### Testing & Demos
- **`test_crypto.py`** - Unit tests for all cryptographic operations
- **`demo_ui.py`** - Demo script showing UI features (work in progress)
- **`screenshots_demo.py`** - Script to generate UI screenshots for documentation

### Build Configuration
- **`.gitignore`** - Git ignore file for Python projects

## `secure_chat/` Package

Main Python package containing all application modules.

### Package Root
- **`__init__.py`** - Package initialization, exports all public classes

## `secure_chat/core/` - Core Functionality

Core business logic and security implementations.

### Files

#### `crypto.py` - Cryptography Module
**Purpose**: All cryptographic operations
**Key Classes**:
- `CryptoManager` - Main cryptography manager

**Features**:
- RSA-2048 key pair generation
- Digital signature creation and verification (RSA-PSS-SHA256)
- Diffie-Hellman key exchange (2048-bit)
- Session key derivation (PBKDF2-HMAC-SHA256)
- AES-256-GCM encryption/decryption
- HMAC-SHA256 for control messages
- Replay attack protection (timestamp + counter)

**Lines of Code**: ~350

#### `key_manager.py` - Key Management Module
**Purpose**: Secure storage and loading of cryptographic keys
**Key Classes**:
- `KeyManager` - Manages key lifecycle

**Features**:
- Creates `~/.secure_chat/` directory structure
- Saves RSA keys with proper permissions (0600 for private)
- Loads existing keys
- Configuration file management
- Log file path management

**Lines of Code**: ~130

#### `network.py` - Network Module
**Purpose**: All network communication (TCP and UDP)
**Key Classes**:
- `NetworkManager` - Network operations manager
- `PeerInfo` - Data class for peer information

**Features**:
- TCP server for incoming connections
- UDP broadcast for peer discovery
- UDP responder for discovery responses
- Message sending/receiving with length prefixes
- Connection management
- Peer discovery protocol

**Lines of Code**: ~280

#### `session.py` - Session Management Module
**Purpose**: Manages secure chat sessions between peers
**Key Classes**:
- `SessionManager` - Session lifecycle manager
- `SessionState` - Enum for session states
- `SessionInfo` - Data class for session information

**Features**:
- Invitation-based connection establishment
- Challenge-response authentication
- Diffie-Hellman key exchange orchestration
- Message encryption/decryption handling
- Automatic key rotation (100 messages or 30 minutes)
- Session timeout management
- Thread-safe operations

**Lines of Code**: ~500

#### `__init__.py`
**Purpose**: Package initialization for core module
**Exports**: CryptoManager, KeyManager, NetworkManager, PeerInfo, SessionManager, SessionState, SessionInfo

## `secure_chat/ui/` - User Interface

Terminal user interface implementation.

### Files

#### `terminal.py` - Terminal UI Module
**Purpose**: Rich-based terminal interface
**Key Classes**:
- `ChatUI` - Main UI manager

**Features**:
- Welcome screen
- Peer discovery display (table format)
- Chat message display with timestamps
- System message notifications
- Status display panel
- Invitation notifications
- Command help screen
- Error and success messages
- Input prompting

**Lines of Code**: ~350

#### `__init__.py`
**Purpose**: Package initialization for UI module
**Exports**: ChatUI

## `secure_chat/utils/` - Utilities

Utility modules for logging and other helpers.

### Files

#### `logger.py` - Security Logger Module
**Purpose**: Security event logging and audit trail
**Key Classes**:
- `SecurityLogger` - Security event logger

**Features**:
- Logs all security-relevant events
- Never logs message content (privacy)
- Structured log format: [Timestamp][Level][Event]
- Logs stored in `~/.secure_chat/logs/security.log`

**Events Logged**:
- Key generation/loading
- Peer discovery
- Connection attempts (success/failure)
- Key exchange (success/failure)
- Message sent/received (no content)
- Key rotation
- Session timeout
- Disconnections
- Attack detection (replay, signature failure)

**Lines of Code**: ~140

#### `__init__.py`
**Purpose**: Package initialization for utils module
**Exports**: SecurityLogger

## Runtime Directory Structure

When the application runs, it creates the following in the user's home directory:

```
~/.secure_chat/
├── keys/
│   ├── private_key.pem    # RSA private key (0600 permissions)
│   └── public_key.pem     # RSA public key (0644 permissions)
├── logs/
│   └── security.log       # Security event audit log
└── config.json            # Optional user configuration
```

## File Statistics

### Total Files: 20

#### By Type:
- Python files: 13
  - Main application: 1
  - Package modules: 8
  - __init__.py files: 4
  - Tests: 1
  - Demos: 2
- Documentation: 3 (README, QUICKSTART, SECURITY)
- Configuration: 3 (requirements.txt, setup.py, config.example.json)
- Other: 1 (.gitignore)

#### Lines of Code (approximate):
- Core modules: ~1,260 lines
- UI module: ~350 lines
- Utils module: ~140 lines
- Main application: ~350 lines
- Tests: ~200 lines
- **Total application code**: ~2,300 lines

#### Documentation:
- README.md: ~550 lines
- QUICKSTART.md: ~350 lines
- SECURITY.md: ~350 lines
- **Total documentation**: ~1,250 lines

## Module Dependencies

```
main.py
  ├── secure_chat.core.CryptoManager
  ├── secure_chat.core.KeyManager
  ├── secure_chat.core.NetworkManager
  ├── secure_chat.core.SessionManager
  ├── secure_chat.ui.ChatUI
  └── secure_chat.utils.SecurityLogger

secure_chat.core.SessionManager
  ├── secure_chat.core.CryptoManager
  └── secure_chat.core.NetworkManager

secure_chat.core.CryptoManager
  └── cryptography (external library)

secure_chat.ui.ChatUI
  └── rich (external library)
```

## External Dependencies

From `requirements.txt`:

1. **cryptography>=41.0.0**
   - Purpose: All cryptographic operations
   - Used by: `crypto.py`
   - Features used: RSA, DH, AES-GCM, PBKDF2, signatures

2. **rich>=13.7.0**
   - Purpose: Terminal UI rendering
   - Used by: `terminal.py`
   - Features used: Console, Panel, Table, Text styling

## Design Patterns Used

1. **Manager Pattern**: CryptoManager, KeyManager, NetworkManager, SessionManager
2. **Observer Pattern**: Callbacks for events (on_message_received, on_state_changed)
3. **State Pattern**: SessionState enum for session lifecycle
4. **Singleton-like**: Single instances of managers per application
5. **Thread-Safe Patterns**: Locks for critical sections (rekey_lock)
6. **Resource Management**: try-finally for socket cleanup

## Testing

- **`test_crypto.py`**: Comprehensive tests for all cryptographic operations
- Test coverage: All core crypto functions
- Test types: Unit tests with assertions
- Test execution: Simple `python test_crypto.py`

## Key Features by File

| File | Key Features |
|------|-------------|
| `crypto.py` | RSA, DH, AES-GCM, HMAC, Signatures |
| `key_manager.py` | Key storage, directory management |
| `network.py` | TCP sockets, UDP discovery |
| `session.py` | Connection lifecycle, key exchange |
| `terminal.py` | Rich UI, message display |
| `logger.py` | Security audit trail |
| `main.py` | Application orchestration |

## Future Enhancements

Potential files/modules to add:
- `secure_chat/core/config.py` - Configuration management
- `secure_chat/utils/validation.py` - Input validation
- `secure_chat/core/protocol.py` - Protocol message definitions
- `tests/test_network.py` - Network module tests
- `tests/test_session.py` - Session module tests
- `secure_chat/ui/gui.py` - Optional GUI interface

---

**Last Updated**: 2026-01-29  
**Total Project Size**: ~3,550 lines (code + docs)  
**Status**: ✅ Complete and tested
