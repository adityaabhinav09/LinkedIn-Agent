"""Main LangGraph agent for LinkedIn AI posting."""

from typing import Dict, Any, TypedDict, Literal
from langgraph.graph import StateGraph, END
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.nodes import ContentGeneratorNode, ApprovalHandlerNode, LinkedInPosterNode
from src.utils.storage import StorageManager


class AgentState(TypedDict, total=False):
    """State schema for the LinkedIn posting agent."""
    # Input
    current_day: int
    auto_approve: bool
    regenerate_feedback: str
    
    # Content generation
    generated_content: Dict[str, Any]
    needs_approval: bool
    
    # Approval
    approval_result: Dict[str, Any]
    
    # Posting
    posting_result: Dict[str, Any]
    
    # Control flow
    needs_regeneration: bool
    workflow_complete: bool
    quit_requested: bool
    error: str


class LinkedInPostingAgent:
    """
    LangGraph agent for automated LinkedIn posting with approval workflow.
    
    The agent follows this flow:
    1. Generate content based on curriculum
    2. Present content for user approval
    3. Post to LinkedIn if approved, or regenerate if rejected
    """
    
    def __init__(self, use_mock_api: bool = False):
        """
        Initialize the agent.
        
        Args:
            use_mock_api: If True, use mock LinkedIn API for testing
        """
        self.storage = StorageManager()
        self.use_mock_api = use_mock_api
        
        # Initialize nodes
        self.content_generator = ContentGeneratorNode()
        self.approval_handler = ApprovalHandlerNode()
        self.linkedin_poster = LinkedInPosterNode(use_mock=use_mock_api)
        
        # Build the graph
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Configured StateGraph
        """
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("generate_content", self.content_generator)
        workflow.add_node("get_approval", self.approval_handler)
        workflow.add_node("post_to_linkedin", self.linkedin_poster)
        
        # Add edges
        workflow.set_entry_point("generate_content")
        
        workflow.add_conditional_edges(
            "generate_content",
            self._route_after_generation,
            {
                "needs_approval": "get_approval",
                "error": END
            }
        )
        
        workflow.add_edge("get_approval", "post_to_linkedin")
        
        workflow.add_conditional_edges(
            "post_to_linkedin",
            self._route_after_posting,
            {
                "regenerate": "generate_content",
                "complete": END
            }
        )
        
        return workflow
    
    def _route_after_generation(self, state: AgentState) -> Literal["needs_approval", "error"]:
        """Route after content generation."""
        content = state.get("generated_content", {})
        
        if content.get("success"):
            return "needs_approval"
        return "error"
    
    def _route_after_posting(self, state: AgentState) -> Literal["regenerate", "complete"]:
        """Route after posting attempt."""
        if state.get("needs_regeneration"):
            return "regenerate"
        return "complete"
    
    def run(self, day: int = None, auto_approve: bool = False) -> Dict[str, Any]:
        """
        Run the posting workflow for a specific day.
        
        Args:
            day: Day number (defaults to current day in journey)
            auto_approve: If True, skip approval step
            
        Returns:
            Final state after workflow completion
        """
        if day is None:
            day = self.storage.get_current_day()
        
        initial_state: AgentState = {
            "current_day": day,
            "auto_approve": auto_approve,
            "workflow_complete": False
        }
        
        # Run the workflow
        final_state = self.app.invoke(initial_state)
        
        return final_state
    
    def preview_post(self, day: int = None) -> Dict[str, Any]:
        """
        Generate and preview a post without posting.
        
        Args:
            day: Day number
            
        Returns:
            Generated content
        """
        if day is None:
            day = self.storage.get_current_day()
        
        return self.content_generator.generate_post(day)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status.
        
        Returns:
            Status information
        """
        progress = self.storage.get_progress()
        current_topic = self.storage.get_topic_for_day(progress["current_day"])
        
        return {
            **progress,
            "current_topic": current_topic["topic"] if current_topic else None,
            "current_category": current_topic["category"] if current_topic else None,
            "pending_approval": self.storage.get_pending_approval()
        }
    
    def get_history(self, last_n: int = 10) -> list:
        """
        Get posting history.
        
        Args:
            last_n: Number of recent posts to return
            
        Returns:
            List of posted items
        """
        return self.storage.get_recent_posts(last_n)


def create_agent(use_mock: bool = False) -> LinkedInPostingAgent:
    """
    Factory function to create the agent.
    
    Args:
        use_mock: Use mock LinkedIn API
        
    Returns:
        Configured LinkedInPostingAgent
    """
    return LinkedInPostingAgent(use_mock_api=use_mock)
