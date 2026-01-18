"""
LinkedIn AI Concepts Posting Agent
==================================

A LangGraph-based agent that posts daily AI concepts on LinkedIn,
progressing from basics to advanced topics over 90 days.

Usage:
    python main.py

Commands:
    start    - Start the 90-day posting schedule
    generate - Generate today's post for preview
    post     - Generate and post (with approval)
    approve  - Approve pending content
    status   - View current progress
    history  - View posting history
    reset    - Reset the journey (caution!)
    help     - Show available commands
    quit     - Exit the agent
"""

import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import POSTING_TIME, LINKEDIN_ACCESS_TOKEN, OLLAMA_MODEL, OLLAMA_BASE_URL
from src.agent import create_agent, LinkedInPostingAgent
from src.utils.storage import StorageManager
from src.utils.scheduler import Scheduler


console = Console()


def print_banner():
    """Print the application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║          🤖 LinkedIn AI Concepts Agent 🤖                      ║
    ║                                                               ║
    ║     90-Day Journey from AI Basics to Advanced Topics          ║
    ║           Story-style posts with daily approval               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="cyan")


def print_status(agent: LinkedInPostingAgent):
    """Print current agent status."""
    status = agent.get_status()
    
    table = Table(title="📊 Current Status", show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Current Day", f"{status['current_day']}/90")
    table.add_row("Total Posts", str(status['total_posts']))
    table.add_row("Completion", f"{status['completion_percentage']}%")
    table.add_row("Status", status['status'])
    table.add_row("Today's Topic", status['current_topic'] or "N/A")
    table.add_row("Category", status['current_category'] or "N/A")
    
    if status['last_post_date']:
        table.add_row("Last Posted", status['last_post_date'][:10])
    
    if status['pending_approval']:
        table.add_row("Pending", "⚠️ Content awaiting approval")
    
    console.print()
    console.print(table)
    console.print()


def print_history(agent: LinkedInPostingAgent, count: int = 10):
    """Print posting history."""
    history = agent.get_history(count)
    
    if not history:
        console.print("[yellow]No posts yet. Start your journey![/yellow]")
        return
    
    table = Table(title=f"📜 Last {len(history)} Posts")
    table.add_column("Day", style="cyan", width=5)
    table.add_column("Topic", style="white", width=40)
    table.add_column("Posted At", style="dim", width=12)
    table.add_column("Chars", style="dim", width=6)
    
    for post in reversed(history):
        table.add_row(
            str(post['day']),
            post['topic'][:38] + "..." if len(post['topic']) > 40 else post['topic'],
            post['posted_at'][:10],
            str(post['char_count'])
        )
    
    console.print()
    console.print(table)
    console.print()


def check_configuration():
    """Check if all required configuration is present."""
    issues = []
    
    # Check Ollama connection
    import requests
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            if any(OLLAMA_MODEL in m for m in models):
                console.print(f"[green]✓ Ollama running with model: {OLLAMA_MODEL}[/green]")
            else:
                console.print(f"[yellow]⚠️ Model '{OLLAMA_MODEL}' not found. Available: {', '.join(models[:5])}[/yellow]")
                console.print(f"[dim]Run: ollama pull {OLLAMA_MODEL}[/dim]")
        else:
            issues.append("❌ Ollama not responding")
    except requests.exceptions.RequestException:
        issues.append("❌ Ollama not running at " + OLLAMA_BASE_URL)
        console.print("[red]❌ Ollama not running. Start it with: ollama serve[/red]")
    
    if not LINKEDIN_ACCESS_TOKEN:
        issues.append("⚠️  LINKEDIN_ACCESS_TOKEN not set (will use mock API)")
        console.print("[yellow]⚠️  LinkedIn credentials not set - using mock mode[/yellow]")
    else:
        console.print("[green]✓ LinkedIn credentials configured[/green]")
    
    return len([i for i in issues if i.startswith("❌")]) == 0


def run_scheduled_mode(agent: LinkedInPostingAgent):
    """Run the agent in scheduled mode with daily triggers at 10 AM."""
    console.print(f"\n[cyan]🕐 Scheduled mode activated[/cyan]")
    console.print(f"[dim]Posts will be generated for approval at {POSTING_TIME} daily[/dim]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    
    scheduler = Scheduler(POSTING_TIME)
    
    def daily_trigger():
        console.print(f"\n[bold cyan]🔔 It's posting time! ({datetime.now().strftime('%H:%M')})[/bold cyan]")
        agent.run()
    
    scheduler.schedule_daily(daily_trigger)
    scheduler.start()
    
    try:
        # Keep the main thread running and allow manual commands
        while True:
            next_run = scheduler.time_until_next_run()
            if next_run:
                console.print(f"[dim]Next post in: {scheduler.format_time_remaining(next_run)}[/dim]")
            
            command = Prompt.ask(
                "\n[dim]Enter command (or wait for scheduled time)[/dim]",
                default="status"
            ).lower().strip()
            
            if command == "status":
                print_status(agent)
            elif command == "now":
                agent.run()
            elif command == "quit":
                break
            elif command == "help":
                print_commands()
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.stop()
        console.print("\n[yellow]Scheduler stopped.[/yellow]")


def run_interactive_mode(agent: LinkedInPostingAgent):
    """Run the agent in interactive mode."""
    storage = StorageManager()
    
    while True:
        console.print("\n[bold cyan]Commands:[/bold cyan] generate | post | status | history | schedule | curriculum | reset | help | quit")
        command = Prompt.ask("Enter command", default="status").lower().strip()
        
        if command == "quit" or command == "q":
            console.print("[dim]Goodbye! Keep learning AI! 🚀[/dim]")
            break
        
        elif command == "status" or command == "s":
            print_status(agent)
        
        elif command == "generate" or command == "g":
            day = storage.get_current_day()
            console.print(f"\n[cyan]Generating preview for Day {day}...[/cyan]")
            result = agent.preview_post(day)
            
            if result.get("success"):
                console.print(Panel(result['content'], title=f"Day {day}: {result['topic']}", border_style="green"))
                console.print(f"[dim]Characters: {result['char_count']}[/dim]")
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif command == "post" or command == "p":
            console.print("\n[cyan]Starting posting workflow...[/cyan]")
            result = agent.run()
            
            if result.get("quit_requested"):
                continue
            
            if result.get("posting_result", {}).get("success"):
                console.print("\n[green]✅ Workflow completed successfully![/green]")
            elif result.get("posting_result", {}).get("action") == "skipped":
                console.print("\n[yellow]Post skipped.[/yellow]")
        
        elif command == "history" or command == "h":
            count = Prompt.ask("How many posts to show?", default="10")
            print_history(agent, int(count))
        
        elif command == "schedule":
            run_scheduled_mode(agent)
        
        elif command == "curriculum" or command == "c":
            show_curriculum(storage)
        
        elif command == "reset":
            if Confirm.ask("[red]⚠️  This will reset ALL progress. Are you sure?[/red]", default=False):
                storage.reset_journey()
                console.print("[green]Journey reset. Starting fresh![/green]")
        
        elif command == "help":
            print_commands()
        
        else:
            console.print(f"[yellow]Unknown command: {command}[/yellow]")
            print_commands()


def show_curriculum(storage: StorageManager):
    """Display the 90-day curriculum."""
    topics = storage.get_all_topics()
    posted_days = storage.get_posted_days()
    current_day = storage.get_current_day()
    
    # Group by category
    categories = {}
    for topic in topics:
        cat = topic['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(topic)
    
    console.print("\n[bold cyan]📚 90-Day AI Curriculum[/bold cyan]\n")
    
    for category, items in categories.items():
        console.print(f"\n[bold yellow]{category}[/bold yellow]")
        for item in items:
            day = item['day']
            status = "✅" if day in posted_days else ("📍" if day == current_day else "⬜")
            difficulty_color = {"Beginner": "green", "Intermediate": "yellow", "Advanced": "red"}.get(item['difficulty'], "white")
            console.print(f"  {status} Day {day:2d}: [{difficulty_color}]{item['topic']}[/{difficulty_color}]")


def print_commands():
    """Print available commands."""
    commands = """
    [bold]Available Commands:[/bold]
    
    [cyan]generate[/cyan] (g)  - Generate and preview today's post
    [cyan]post[/cyan] (p)      - Generate, approve, and post
    [cyan]status[/cyan] (s)    - Show current progress
    [cyan]history[/cyan] (h)   - Show posting history
    [cyan]schedule[/cyan]      - Start scheduled posting mode (10 AM daily)
    [cyan]curriculum[/cyan] (c)- View full 90-day curriculum
    [cyan]reset[/cyan]         - Reset journey (caution!)
    [cyan]help[/cyan]          - Show this help message
    [cyan]quit[/cyan] (q)      - Exit the application
    """
    console.print(commands)


def main():
    """Main entry point."""
    print_banner()
    
    # Check configuration
    console.print("\n[bold]Checking configuration...[/bold]\n")
    if not check_configuration():
        console.print("\n[red]Please configure the required settings in .env file[/red]")
        console.print("[dim]Copy .env.example to .env and fill in your credentials[/dim]")
        return
    
    # Determine if we should use mock API
    use_mock = not LINKEDIN_ACCESS_TOKEN
    
    # Create agent
    console.print("\n[cyan]Initializing agent...[/cyan]")
    agent = create_agent(use_mock=use_mock)
    
    # Show initial status
    print_status(agent)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "schedule":
            run_scheduled_mode(agent)
        elif command == "post":
            agent.run()
        elif command == "status":
            print_status(agent)
        else:
            run_interactive_mode(agent)
    else:
        run_interactive_mode(agent)


if __name__ == "__main__":
    main()
