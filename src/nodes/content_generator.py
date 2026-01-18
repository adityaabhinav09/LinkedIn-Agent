"""Content generator node for creating LinkedIn posts."""

from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from pathlib import Path
import sys
import time

sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL, MAX_POST_LENGTH
from src.prompts.templates import STORY_GENERATION_PROMPT, HASHTAG_PROMPT
from src.utils.storage import StorageManager


class ContentGeneratorNode:
    """Node responsible for generating story-style LinkedIn posts."""
    
    def __init__(self):
        """Initialize the content generator."""
        self.llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            temperature=0.8,  # Higher for creativity
        )
        self.storage = StorageManager()
    
    def _invoke_with_retry(self, messages, max_retries=3):
        """Invoke LLM with retry logic for rate limits."""
        for attempt in range(max_retries):
            try:
                return self.llm.invoke(messages)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = 30 * (attempt + 1)  # 30s, 60s, 90s
                    print(f"\n⏳ Rate limited. Waiting {wait_time}s before retry ({attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    raise e
        raise Exception("Max retries exceeded due to rate limiting")
    
    def generate_post(self, day: int) -> Dict[str, Any]:
        """
        Generate a LinkedIn post for a specific day.
        
        Args:
            day: The day number (1-90)
            
        Returns:
            Dict containing generated content and metadata
        """
        # Get topic for the day
        topic_info = self.storage.get_topic_for_day(day)
        
        if not topic_info:
            return {
                "success": False,
                "error": f"No topic found for day {day}"
            }
        
        # Check if already posted
        if self.storage.is_day_posted(day):
            return {
                "success": False,
                "error": f"Day {day} has already been posted",
                "duplicate": True
            }
        
        # Get context from previous posts
        previous_posts_summary = self.storage.get_recent_posts_summary(3)
        
        # Format the prompt
        prompt = STORY_GENERATION_PROMPT.format(
            day=day,
            topic=topic_info["topic"],
            category=topic_info["category"],
            difficulty=topic_info["difficulty"],
            key_points=", ".join(topic_info["key_points"]),
            story_angle=topic_info["story_angle"],
            previous_posts_summary=previous_posts_summary
        )
        
        # Generate content
        messages = [
            SystemMessage(content="You are an expert AI educator creating engaging LinkedIn content."),
            HumanMessage(content=prompt)
        ]
        
        response = self._invoke_with_retry(messages)
        content = response.content
        
        # Ensure content is within limits
        if len(content) > MAX_POST_LENGTH:
            content = self._truncate_content(content)
        
        # Generate hashtags if not already present
        if "#" not in content[-200:]:  # Check last 200 chars for hashtags
            hashtags = self._generate_hashtags(content)
            content = f"{content}\n\n---\n{hashtags}"
        
        return {
            "success": True,
            "day": day,
            "topic": topic_info["topic"],
            "category": topic_info["category"],
            "difficulty": topic_info["difficulty"],
            "content": content,
            "char_count": len(content)
        }
    
    def _generate_hashtags(self, content: str) -> str:
        """Generate relevant hashtags for the post."""
        prompt = HASHTAG_PROMPT.format(post_content=content[:500])
        
        messages = [
            HumanMessage(content=prompt)
        ]
        
        response = self._invoke_with_retry(messages)
        return response.content.strip()
    
    def _truncate_content(self, content: str) -> str:
        """Truncate content to fit within LinkedIn limits."""
        if len(content) <= MAX_POST_LENGTH:
            return content
        
        # Find a good break point
        truncated = content[:MAX_POST_LENGTH - 100]
        
        # Try to end at a paragraph
        last_para = truncated.rfind('\n\n')
        if last_para > len(truncated) * 0.7:
            truncated = truncated[:last_para]
        
        return truncated
    
    def regenerate_post(self, day: int, feedback: str = None) -> Dict[str, Any]:
        """
        Regenerate a post with optional feedback.
        
        Args:
            day: The day number
            feedback: Optional feedback for improvement
            
        Returns:
            New generated content
        """
        topic_info = self.storage.get_topic_for_day(day)
        
        if not topic_info:
            return {
                "success": False,
                "error": f"No topic found for day {day}"
            }
        
        previous_posts_summary = self.storage.get_recent_posts_summary(3)
        
        # Add feedback to prompt if provided
        prompt = STORY_GENERATION_PROMPT.format(
            day=day,
            topic=topic_info["topic"],
            category=topic_info["category"],
            difficulty=topic_info["difficulty"],
            key_points=", ".join(topic_info["key_points"]),
            story_angle=topic_info["story_angle"],
            previous_posts_summary=previous_posts_summary
        )
        
        if feedback:
            prompt += f"\n\n## Additional Feedback:\n{feedback}\n\nPlease incorporate this feedback in the new version."
        
        messages = [
            SystemMessage(content="You are an expert AI educator. Create a DIFFERENT version of this post with fresh perspective."),
            HumanMessage(content=prompt)
        ]
        
        response = self._invoke_with_retry(messages)
        content = response.content
        
        if len(content) > MAX_POST_LENGTH:
            content = self._truncate_content(content)
        
        if "#" not in content[-200:]:
            hashtags = self._generate_hashtags(content)
            content = f"{content}\n\n---\n{hashtags}"
        
        return {
            "success": True,
            "day": day,
            "topic": topic_info["topic"],
            "category": topic_info["category"],
            "difficulty": topic_info["difficulty"],
            "content": content,
            "char_count": len(content),
            "regenerated": True
        }
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph node entry point.
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with generated content
        """
        day = state.get("current_day", self.storage.get_current_day())
        feedback = state.get("regenerate_feedback")
        
        if feedback:
            result = self.regenerate_post(day, feedback)
        else:
            result = self.generate_post(day)
        
        state["generated_content"] = result
        state["needs_approval"] = result.get("success", False)
        
        return state
