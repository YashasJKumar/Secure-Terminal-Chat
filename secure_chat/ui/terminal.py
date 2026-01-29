"""
Terminal UI module using Rich library for better terminal experience.
"""

import threading
from typing import Optional, List, Callable
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt

from ..core.network import PeerInfo
from ..core.session import SessionState


class ChatUI:
    """Rich-based terminal user interface for chat application."""
    
    def __init__(self):
        """Initialize chat UI."""
        self.console = Console()
        self.messages: List[tuple] = []  # (timestamp, sender, message)
        self.status_text = "Disconnected"
        self.peer_info = ""
        self.encryption_status = "❌ No encryption"
        self.input_prompt = "> "
        self.live: Optional[Live] = None
        self.running = False
        self.on_command: Optional[Callable[[str], None]] = None
        
    def start(self):
        """Start the UI."""
        self.running = True
        self.console.clear()
        
    def stop(self):
        """Stop the UI."""
        self.running = False
        
    def show_welcome(self):
        """Show welcome screen."""
        self.console.clear()
        welcome_text = """
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

[yellow]Available Commands:[/yellow]
  /discover    - Scan for peers on network
  /connect <#> - Send connection invitation to peer number
  /accept      - Accept incoming invitation
  /reject      - Reject incoming invitation
  /disconnect  - End current session
  /rekey       - Force session key rotation
  /status      - Show security status
  /help        - Show this help
  /quit        - Exit application

Press Enter to continue...
"""
        self.console.print(welcome_text)
        input()
        
    def show_peers(self, peers: List[PeerInfo]):
        """
        Display list of discovered peers.
        
        Args:
            peers: List of discovered peers
        """
        self.console.clear()
        
        if not peers:
            self.console.print("\n[yellow]No peers discovered on the network.[/yellow]\n")
            return
        
        table = Table(title="📡 Discovered Peers", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Peer ID", style="cyan")
        table.add_column("IP Address", style="green")
        table.add_column("Port", style="yellow")
        
        for idx, peer in enumerate(peers, 1):
            table.add_row(
                str(idx),
                peer.peer_id,
                peer.address,
                str(peer.port)
            )
        
        self.console.print(table)
        self.console.print("\nUse [bold]/connect <#>[/bold] to connect to a peer\n")
        
    def show_status(self, status: dict):
        """
        Show current session status.
        
        Args:
            status: Status dictionary
        """
        self.console.clear()
        
        status_panel = Panel(
            self._format_status(status),
            title="🔐 Security Status",
            border_style="cyan"
        )
        
        self.console.print(status_panel)
        self.console.print()
        
    def _format_status(self, status: dict) -> str:
        """Format status information."""
        lines = []
        
        state = status.get('state', 'disconnected')
        lines.append(f"[bold]Connection State:[/bold] {state}")
        
        if state != 'disconnected':
            lines.append(f"[bold]Peer ID:[/bold] {status.get('peer_id', 'N/A')}")
            lines.append(f"[bold]Peer Address:[/bold] {status.get('peer_address', 'N/A')}")
            
            if status.get('established_at'):
                est_time = datetime.fromtimestamp(status['established_at']).strftime('%H:%M:%S')
                lines.append(f"[bold]Connected Since:[/bold] {est_time}")
            
            lines.append(f"[bold]Messages Sent:[/bold] {status.get('messages_sent', 0)}")
            
            if status.get('session_key_active'):
                lines.append(f"[bold]Encryption:[/bold] [green]✓ Active (AES-256-GCM)[/green]")
            else:
                lines.append(f"[bold]Encryption:[/bold] [red]✗ Inactive[/red]")
        else:
            lines.append("[yellow]No active session[/yellow]")
        
        return "\n".join(lines)
    
    def add_message(self, sender: str, message: str):
        """
        Add message to chat history.
        
        Args:
            sender: Message sender ('You' or peer ID)
            message: Message text
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.messages.append((timestamp, sender, message))
        
        # Keep only last 100 messages
        if len(self.messages) > 100:
            self.messages = self.messages[-100:]
        
        # Display in console
        if sender == "You":
            self.console.print(f"[dim]{timestamp}[/dim] [bold cyan]You:[/bold cyan] {message}")
        else:
            self.console.print(f"[dim]{timestamp}[/dim] [bold green]{sender}:[/bold green] {message}")
    
    def add_system_message(self, message: str, style: str = "yellow"):
        """
        Add system message.
        
        Args:
            message: System message
            style: Rich style for the message
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.console.print(f"[dim]{timestamp}[/dim] [bold {style}]System:[/bold {style}] {message}")
    
    def show_invitation(self, peer_id: str, address: str):
        """
        Show incoming invitation notification.
        
        Args:
            peer_id: Peer ID
            address: Peer address
        """
        self.console.print()
        invitation_panel = Panel(
            f"[bold]Peer ID:[/bold] {peer_id}\n[bold]Address:[/bold] {address}\n\n"
            f"Use [bold cyan]/accept[/bold cyan] to accept or [bold red]/reject[/bold red] to reject",
            title="📨 Incoming Connection Invitation",
            border_style="yellow"
        )
        self.console.print(invitation_panel)
        self.console.print()
    
    def prompt_input(self) -> str:
        """
        Prompt for user input.
        
        Returns:
            User input
        """
        try:
            return Prompt.ask("[bold cyan]>[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            return "/quit"
    
    def show_error(self, message: str):
        """
        Show error message.
        
        Args:
            message: Error message
        """
        self.console.print(f"[bold red]Error:[/bold red] {message}")
    
    def show_success(self, message: str):
        """
        Show success message.
        
        Args:
            message: Success message
        """
        self.console.print(f"[bold green]Success:[/bold green] {message}")
    
    def show_help(self):
        """Show help information."""
        self.console.clear()
        help_text = """
[bold cyan]═══════════════════════════════════════════════════════════
                    COMMAND REFERENCE
═══════════════════════════════════════════════════════════[/bold cyan]

[yellow]Network Commands:[/yellow]
  [bold]/discover[/bold]      - Scan for peers on the local network
                    Uses UDP broadcast to find active peers
  
  [bold]/connect <#>[/bold]   - Send connection invitation to peer
                    Use the peer number from /discover list

[yellow]Connection Commands:[/yellow]
  [bold]/accept[/bold]        - Accept incoming connection invitation
                    Initiates key exchange with peer
  
  [bold]/reject[/bold]        - Reject incoming connection invitation
  
  [bold]/disconnect[/bold]    - End current chat session
                    Closes connection and clears session keys

[yellow]Security Commands:[/yellow]
  [bold]/rekey[/bold]         - Force session key rotation
                    Generates new session key via DH exchange
  
  [bold]/status[/bold]        - Show detailed security status
                    Displays encryption state and session info

[yellow]General Commands:[/yellow]
  [bold]/help[/bold]          - Show this help message
  
  [bold]/quit[/bold]          - Exit the application

[yellow]Sending Messages:[/yellow]
  Simply type your message and press Enter when connected.
  All messages are encrypted end-to-end with AES-256-GCM.

[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]

Press Enter to continue...
"""
        self.console.print(help_text)
        input()
