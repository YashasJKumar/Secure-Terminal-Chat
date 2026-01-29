#!/usr/bin/env python3
"""
Simple screenshot demo of the Secure Terminal Chat UI.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def show_welcome():
    """Show welcome screen."""
    console.print("""
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
  /connect <#> - Send connection invitation to peer
  /accept      - Accept incoming invitation
  /disconnect  - End current session
  /rekey       - Force session key rotation
  /status      - Show security status
  /quit        - Exit application
""")


def show_peer_discovery():
    """Show peer discovery table."""
    console.print()
    table = Table(title="📡 Discovered Peers", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Peer ID", style="cyan")
    table.add_column("IP Address", style="green")
    table.add_column("Port", style="yellow")
    
    table.add_row("1", "peer_abc123", "192.168.1.100", "50001")
    table.add_row("2", "peer_xyz789", "192.168.1.101", "50002")
    table.add_row("3", "peer_def456", "192.168.1.102", "50003")
    
    console.print(table)
    console.print("\n[dim]Use [bold]/connect <#>[/bold] to connect to a peer[/dim]\n")


def show_chat_session():
    """Show a sample chat session."""
    console.print("\n[bold cyan]Chat Session:[/bold cyan]\n")
    
    messages = [
        ("[dim]14:23:15[/dim] [bold yellow]System:[/bold yellow] Your Peer ID: peer_demo123", None),
        ("[dim]14:23:15[/dim] [bold yellow]System:[/bold yellow] Listening on port: 50001", None),
        ("[dim]14:23:22[/dim] [bold yellow]System:[/bold yellow] Scanning for peers...", None),
        ("[dim]14:23:24[/dim] [bold green]System:[/bold green] ✓ Connected and encrypted", None),
        ("[dim]14:23:30[/dim] [bold cyan]You:[/bold cyan] Hello! This is a secure message.", None),
        ("[dim]14:23:32[/dim] [bold green]peer_abc123:[/bold green] Hi! I received your encrypted message.", None),
        ("[dim]14:23:35[/dim] [bold cyan]You:[/bold cyan] All messages are encrypted with AES-256-GCM.", None),
        ("[dim]14:23:37[/dim] [bold green]peer_abc123:[/bold green] Perfect forward secrecy is enabled!", None),
    ]
    
    for msg, _ in messages:
        console.print(msg)


def show_invitation():
    """Show incoming invitation."""
    console.print()
    invitation_panel = Panel(
        "[bold]Peer ID:[/bold] peer_xyz789\n"
        "[bold]Address:[/bold] 192.168.1.101\n\n"
        "Use [bold cyan]/accept[/bold cyan] to accept or [bold red]/reject[/bold red] to reject",
        title="📨 Incoming Connection Invitation",
        border_style="yellow"
    )
    console.print(invitation_panel)
    console.print()


def show_status():
    """Show security status."""
    console.print()
    status_text = """[bold]Connection State:[/bold] connected
[bold]Peer ID:[/bold] peer_abc123
[bold]Peer Address:[/bold] 192.168.1.100
[bold]Connected Since:[/bold] 14:23:24
[bold]Messages Sent:[/bold] 42
[bold]Encryption:[/bold] [green]✓ Active (AES-256-GCM)[/green]"""
    
    status_panel = Panel(
        status_text,
        title="🔐 Security Status",
        border_style="cyan"
    )
    console.print(status_panel)
    console.print()


def main():
    """Run all demos."""
    console.print("\n[bold]═══════════════════════════════════════════════════════════[/bold]")
    console.print("[bold cyan]     SECURE TERMINAL CHAT - UI SCREENSHOTS[/bold cyan]")
    console.print("[bold]═══════════════════════════════════════════════════════════[/bold]\n")
    
    console.print("\n[bold]1. WELCOME SCREEN[/bold]")
    console.print("─" * 63)
    show_welcome()
    
    console.print("\n[bold]2. PEER DISCOVERY[/bold]")
    console.print("─" * 63)
    show_peer_discovery()
    
    console.print("\n[bold]3. CHAT SESSION[/bold]")
    console.print("─" * 63)
    show_chat_session()
    
    console.print("\n[bold]4. INCOMING INVITATION[/bold]")
    console.print("─" * 63)
    show_invitation()
    
    console.print("\n[bold]5. SECURITY STATUS[/bold]")
    console.print("─" * 63)
    show_status()
    
    console.print("[bold]═══════════════════════════════════════════════════════════[/bold]\n")


if __name__ == '__main__':
    main()
