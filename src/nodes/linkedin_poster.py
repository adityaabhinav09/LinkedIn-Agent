"""LinkedIn poster node for publishing approved content."""

from typing import Dict, Any
from datetime import datetime
from rich.console import Console
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.tools.linkedin_api import LinkedInAPI, MockLinkedInAPI
from src.utils.storage import StorageManager
from config.settings import LINKEDIN_ACCESS_TOKEN


console = Console()


class LinkedInPosterNode:
    """Node responsible for posting approved content to LinkedIn."""
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize LinkedIn poster.
        
        Args:
            use_mock: If True, use mock API (for testing)
        """
        self.storage = StorageManager()
        
        # Use mock if no credentials or explicitly requested
        if use_mock or not LINKEDIN_ACCESS_TOKEN:
            self.api = MockLinkedInAPI()
            self.is_mock = True
            console.print("[yellow]⚠️  Using mock LinkedIn API (no credentials configured)[/yellow]")
        else:
            self.api = LinkedInAPI()
            self.is_mock = False
    
    def verify_connection(self) -> bool:
        """
        Verify LinkedIn API connection.
        
        Returns:
            True if connection is valid
        """
        result = self.api.verify_credentials()
        
        if result.get("valid"):
            profile = result.get("profile", {})
            console.print(
                f"[green]✓ Connected as: {profile.get('firstName')} {profile.get('lastName')}[/green]"
            )
            return True
        else:
            console.print(f"[red]✗ Connection failed: {result.get('error')}[/red]")
            return False
    
    def post_content(self, content: str, day: int, topic: str) -> Dict[str, Any]:
        """
        Post content to LinkedIn.
        
        Args:
            content: The post content
            day: Day number
            topic: Topic name
            
        Returns:
            Posting result
        """
        console.print("\n[bold cyan]📤 Posting to LinkedIn...[/bold cyan]")
        
        # Post to LinkedIn
        result = self.api.create_text_post(content)
        
        if result.get("success"):
            post_id = result.get("post_id", "")
            
            # Record in history
            self.storage.add_to_history(
                day=day,
                topic=topic,
                content=content,
                linkedin_post_id=post_id
            )
            
            # Update state
            self.storage.mark_post_completed(day)
            self.storage.clear_pending_approval()
            
            if self.is_mock:
                console.print(f"[yellow]📝 [MOCK] Post simulated successfully![/yellow]")
            else:
                console.print(f"[green]✅ Posted successfully![/green]")
                console.print(f"[dim]Post ID: {post_id}[/dim]")
            
            return {
                "success": True,
                "post_id": post_id,
                "day": day,
                "topic": topic,
                "posted_at": datetime.now().isoformat(),
                "is_mock": self.is_mock
            }
        else:
            console.print(f"[red]❌ Failed to post: {result.get('error')}[/red]")
            if result.get("detail"):
                console.print(f"[dim]Details: {result.get('detail')}[/dim]")
            
            return {
                "success": False,
                "error": result.get("error"),
                "detail": result.get("detail")
            }
    
    def handle_skip(self, day: int, topic: str) -> Dict[str, Any]:
        """
        Handle skipping a day's post.
        
        Args:
            day: Day number
            topic: Topic name
            
        Returns:
            Skip result
        """
        console.print(f"\n[yellow]⏭️  Skipping Day {day}: {topic}[/yellow]")
        
        # Clear pending and move to next day
        self.storage.clear_pending_approval()
        self.storage.increment_day()
        
        return {
            "success": True,
            "action": "skipped",
            "day": day,
            "topic": topic
        }
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph node entry point.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with posting result
        """
        approval_result = state.get("approval_result", {})
        decision = approval_result.get("decision")
        
        if decision == "approve":
            result = self.post_content(
                content=approval_result["content"],
                day=approval_result["day"],
                topic=approval_result["topic"]
            )
            state["posting_result"] = result
            state["workflow_complete"] = result.get("success", False)
            
        elif decision == "skip":
            result = self.handle_skip(
                day=approval_result["day"],
                topic=approval_result["topic"]
            )
            state["posting_result"] = result
            state["workflow_complete"] = True
            
        elif decision == "reject":
            # Signal for regeneration
            state["needs_regeneration"] = True
            state["regenerate_feedback"] = approval_result.get("feedback")
            state["workflow_complete"] = False
            
        elif decision == "quit":
            console.print("\n[dim]Exiting without posting...[/dim]")
            state["posting_result"] = {"action": "quit"}
            state["workflow_complete"] = True
            state["quit_requested"] = True
            
        else:
            state["posting_result"] = {
                "success": False,
                "error": f"Unknown decision: {decision}"
            }
            state["workflow_complete"] = True
        
        return state
