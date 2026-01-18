"""Approval handler node for user confirmation before posting."""

from typing import Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.storage import StorageManager
from src.prompts.templates import APPROVAL_MESSAGE_TEMPLATE


console = Console()


class ApprovalHandlerNode:
    """Node responsible for getting user approval before posting."""
    
    def __init__(self):
        """Initialize approval handler."""
        self.storage = StorageManager()
    
    def display_post_for_approval(self, content_data: Dict[str, Any]) -> None:
        """
        Display the generated post in a formatted way.
        
        Args:
            content_data: Generated content data
        """
        console.print("\n")
        console.print("=" * 70)
        console.print(
            Panel(
                f"[bold cyan]📝 DAILY POST READY FOR REVIEW[/bold cyan]\n\n"
                f"[yellow]Day {content_data['day']}/90[/yellow] | "
                f"[green]Topic: {content_data['topic']}[/green]\n"
                f"[blue]Category: {content_data['category']}[/blue] | "
                f"[magenta]Difficulty: {content_data['difficulty']}[/magenta]",
                title="LinkedIn AI Post",
                border_style="cyan"
            )
        )
        
        console.print("\n")
        console.print(Panel(content_data['content'], border_style="white"))
        console.print("\n")
        
        # Stats
        console.print(f"[dim]Character Count: {content_data['char_count']}[/dim]")
        console.print(f"[dim]Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
        console.print("=" * 70)
    
    def get_user_decision(self) -> str:
        """
        Get user's decision on the generated content.
        
        Returns:
            User's choice (approve/reject/edit/skip/quit)
        """
        console.print("\n[bold]Commands:[/bold]")
        console.print("  [green][A]pprove[/green] - Post to LinkedIn")
        console.print("  [yellow][R]eject[/yellow]  - Regenerate content")
        console.print("  [blue][E]dit[/blue]    - Manually edit before posting")
        console.print("  [magenta][S]kip[/magenta]    - Skip today's post")
        console.print("  [red][Q]uit[/red]    - Exit without posting")
        console.print()
        
        choice = Prompt.ask(
            "Your choice",
            choices=["a", "r", "e", "s", "q", "approve", "reject", "edit", "skip", "quit"],
            default="a"
        ).lower()
        
        # Normalize choice
        choice_map = {
            "a": "approve", "approve": "approve",
            "r": "reject", "reject": "reject",
            "e": "edit", "edit": "edit",
            "s": "skip", "skip": "skip",
            "q": "quit", "quit": "quit"
        }
        
        return choice_map.get(choice, "approve")
    
    def get_edit_content(self, original_content: str) -> str:
        """
        Allow user to manually edit content.
        
        Args:
            original_content: The original generated content
            
        Returns:
            Edited content
        """
        console.print("\n[bold yellow]Edit Mode[/bold yellow]")
        console.print("[dim]Enter your edited content. Type 'END' on a new line when done.[/dim]")
        console.print("[dim]Type 'CANCEL' to keep original content.[/dim]\n")
        
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            if line.strip().upper() == "CANCEL":
                return original_content
            lines.append(line)
        
        edited_content = "\n".join(lines)
        
        if not edited_content.strip():
            console.print("[yellow]Empty content, keeping original.[/yellow]")
            return original_content
        
        return edited_content
    
    def get_rejection_feedback(self) -> Optional[str]:
        """
        Get feedback for content regeneration.
        
        Returns:
            Optional feedback string
        """
        console.print("\n[bold yellow]Regeneration Feedback[/bold yellow]")
        console.print("[dim]Provide feedback to improve the next version (or press Enter to skip):[/dim]\n")
        
        feedback = input().strip()
        return feedback if feedback else None
    
    def request_approval(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main approval workflow.
        
        Args:
            content_data: Generated content data
            
        Returns:
            Approval result with decision and any modifications
        """
        self.display_post_for_approval(content_data)
        
        decision = self.get_user_decision()
        
        result = {
            "decision": decision,
            "content": content_data["content"],
            "day": content_data["day"],
            "topic": content_data["topic"]
        }
        
        if decision == "edit":
            result["content"] = self.get_edit_content(content_data["content"])
            result["edited"] = True
            # After editing, ask for final approval
            console.print("\n[bold]Edited content preview:[/bold]")
            console.print(Panel(result["content"], border_style="blue"))
            
            final_choice = Prompt.ask(
                "Post this edited content?",
                choices=["y", "n"],
                default="y"
            )
            
            if final_choice.lower() == "y":
                result["decision"] = "approve"
            else:
                result["decision"] = "reject"
        
        elif decision == "reject":
            result["feedback"] = self.get_rejection_feedback()
        
        # Store pending approval state
        if decision in ["approve", "edit"]:
            self.storage.set_pending_approval({
                "content": result["content"],
                "day": content_data["day"],
                "topic": content_data["topic"],
                "approved_at": datetime.now().isoformat()
            })
        
        return result
    
    def auto_approve(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-approve content (for automated workflows).
        
        Args:
            content_data: Generated content data
            
        Returns:
            Approval result
        """
        return {
            "decision": "approve",
            "content": content_data["content"],
            "day": content_data["day"],
            "topic": content_data["topic"],
            "auto_approved": True
        }
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph node entry point.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with approval decision
        """
        content_data = state.get("generated_content", {})
        
        if not content_data.get("success"):
            state["approval_result"] = {
                "decision": "error",
                "error": content_data.get("error", "Content generation failed")
            }
            return state
        
        # Check if auto-approve mode
        if state.get("auto_approve"):
            result = self.auto_approve(content_data)
        else:
            result = self.request_approval(content_data)
        
        state["approval_result"] = result
        
        return state
