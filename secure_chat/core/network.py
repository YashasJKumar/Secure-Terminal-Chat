"""
Networking module for peer discovery and TCP communication.
"""

import socket
import json
import threading
import time
from typing import Optional, Callable, List, Tuple
from dataclasses import dataclass


@dataclass
class PeerInfo:
    """Information about a discovered peer."""
    peer_id: str
    address: str
    port: int
    public_key: Optional[bytes] = None


class NetworkManager:
    """Manages network communication for the chat application."""
    
    DISCOVERY_PORT = 50000
    DISCOVERY_MESSAGE = b'SECURE_CHAT_DISCOVERY'
    RESPONSE_MESSAGE = b'SECURE_CHAT_RESPONSE'
    
    def __init__(self, peer_id: str, tcp_port: int = 0):
        """
        Initialize network manager.
        
        Args:
            peer_id: Unique identifier for this peer
            tcp_port: TCP port for incoming connections (0 = random)
        """
        self.peer_id = peer_id
        self.tcp_port = tcp_port
        self.tcp_socket: Optional[socket.socket] = None
        self.udp_socket: Optional[socket.socket] = None
        self.discovery_socket: Optional[socket.socket] = None
        self.running = False
        self.discovered_peers: List[PeerInfo] = []
        self.on_peer_discovered: Optional[Callable[[PeerInfo], None]] = None
        self.on_connection_received: Optional[Callable[[socket.socket, str], None]] = None
    
    def start_tcp_server(self) -> int:
        """
        Start TCP server for incoming connections.
        
        Returns:
            Port number the server is listening on
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(('0.0.0.0', self.tcp_port))
        self.tcp_socket.listen(5)
        
        # Get the actual port if random port was requested
        self.tcp_port = self.tcp_socket.getsockname()[1]
        
        self.running = True
        
        # Start accept thread
        accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
        accept_thread.start()
        
        return self.tcp_port
    
    def _accept_connections(self):
        """Accept incoming TCP connections."""
        while self.running and self.tcp_socket:
            try:
                self.tcp_socket.settimeout(1.0)
                client_socket, address = self.tcp_socket.accept()
                if self.on_connection_received:
                    threading.Thread(
                        target=self.on_connection_received,
                        args=(client_socket, address[0]),
                        daemon=True
                    ).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
                break
    
    def start_discovery_responder(self, public_key: bytes):
        """
        Start UDP responder for peer discovery.
        
        Args:
            public_key: This peer's public key to share
        """
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.discovery_socket.bind(('', self.DISCOVERY_PORT))
        
        # Start discovery responder thread
        responder_thread = threading.Thread(
            target=self._discovery_responder,
            args=(public_key,),
            daemon=True
        )
        responder_thread.start()
    
    def _discovery_responder(self, public_key: bytes):
        """Respond to discovery broadcasts."""
        while self.running and self.discovery_socket:
            try:
                self.discovery_socket.settimeout(1.0)
                data, address = self.discovery_socket.recvfrom(1024)
                
                if data == self.DISCOVERY_MESSAGE:
                    # Send response with our info
                    response = {
                        'peer_id': self.peer_id,
                        'tcp_port': self.tcp_port,
                        'public_key': public_key.decode('utf-8')
                    }
                    response_data = self.RESPONSE_MESSAGE + json.dumps(response).encode('utf-8')
                    self.discovery_socket.sendto(response_data, address)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error in discovery responder: {e}")
    
    def discover_peers(self, timeout: float = 2.0) -> List[PeerInfo]:
        """
        Discover peers on the local network using UDP broadcast.
        
        Args:
            timeout: How long to wait for responses
            
        Returns:
            List of discovered peers
        """
        self.discovered_peers = []
        
        # Create UDP socket for discovery
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.settimeout(0.5)
        
        # Send discovery broadcast
        try:
            udp_socket.sendto(
                self.DISCOVERY_MESSAGE,
                ('<broadcast>', self.DISCOVERY_PORT)
            )
        except Exception as e:
            print(f"Error sending discovery broadcast: {e}")
            udp_socket.close()
            return []
        
        # Collect responses
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                data, address = udp_socket.recvfrom(4096)
                
                if data.startswith(self.RESPONSE_MESSAGE):
                    response_json = data[len(self.RESPONSE_MESSAGE):].decode('utf-8')
                    response = json.loads(response_json)
                    
                    # Don't add ourselves
                    if response['peer_id'] != self.peer_id:
                        peer = PeerInfo(
                            peer_id=response['peer_id'],
                            address=address[0],
                            port=response['tcp_port'],
                            public_key=response['public_key'].encode('utf-8')
                        )
                        
                        # Check if peer already discovered
                        if not any(p.peer_id == peer.peer_id for p in self.discovered_peers):
                            self.discovered_peers.append(peer)
                            if self.on_peer_discovered:
                                self.on_peer_discovered(peer)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error receiving discovery response: {e}")
        
        udp_socket.close()
        return self.discovered_peers
    
    def connect_to_peer(self, address: str, port: int) -> Optional[socket.socket]:
        """
        Connect to a peer via TCP.
        
        Args:
            address: Peer's IP address
            port: Peer's TCP port
            
        Returns:
            Connected socket or None on failure
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((address, port))
            sock.settimeout(None)
            return sock
        except Exception as e:
            print(f"Error connecting to peer: {e}")
            return None
    
    def send_message(self, sock: socket.socket, data: bytes) -> bool:
        """
        Send data over TCP socket with length prefix.
        
        Args:
            sock: Socket to send on
            data: Data to send
            
        Returns:
            True on success
        """
        try:
            # Send length prefix (4 bytes) followed by data
            length = len(data).to_bytes(4, 'big')
            sock.sendall(length + data)
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def receive_message(self, sock: socket.socket, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Receive data from TCP socket with length prefix.
        
        Args:
            sock: Socket to receive from
            timeout: Receive timeout in seconds
            
        Returns:
            Received data or None on error
        """
        try:
            if timeout:
                sock.settimeout(timeout)
            
            # Receive length prefix
            length_data = self._recv_exact(sock, 4)
            if not length_data:
                return None
            
            length = int.from_bytes(length_data, 'big')
            
            # Receive actual data
            data = self._recv_exact(sock, length)
            
            if timeout:
                sock.settimeout(None)
            
            return data
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
    
    def _recv_exact(self, sock: socket.socket, n: int) -> Optional[bytes]:
        """
        Receive exactly n bytes from socket.
        
        Args:
            sock: Socket to receive from
            n: Number of bytes to receive
            
        Returns:
            Received bytes or None on error
        """
        data = b''
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def stop(self):
        """Stop all network operations."""
        self.running = False
        
        if self.tcp_socket:
            try:
                self.tcp_socket.close()
            except:
                pass
        
        if self.udp_socket:
            try:
                self.udp_socket.close()
            except:
                pass
        
        if self.discovery_socket:
            try:
                self.discovery_socket.close()
            except:
                pass
