"""
Secure Terminal Chat Application

A secure terminal-based chat application with end-to-end encryption.
"""

__version__ = '1.0.0'
__author__ = 'Secure Chat Team'

from .core import (
    CryptoManager,
    KeyManager,
    NetworkManager,
    PeerInfo,
    SessionManager,
    SessionState,
    SessionInfo,
)
from .ui import ChatUI
from .utils import SecurityLogger

__all__ = [
    'CryptoManager',
    'KeyManager',
    'NetworkManager',
    'PeerInfo',
    'SessionManager',
    'SessionState',
    'SessionInfo',
    'ChatUI',
    'SecurityLogger',
]
