"""Storage manager for handling post history and agent state."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import CURRICULUM_FILE, HISTORY_FILE, STATE_FILE, DATA_DIR


class StorageManager:
    """Manages persistence for the LinkedIn posting agent."""
    
    def __init__(self):
        """Initialize storage manager and ensure data files exist."""
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure all required data files exist."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        if not HISTORY_FILE.exists():
            self._write_json(HISTORY_FILE, {
                "posted_items": [],
                "last_updated": None,
                "total_posts": 0
            })
        
        if not STATE_FILE.exists():
            self._write_json(STATE_FILE, {
                "current_day": 1,
                "started_at": None,
                "last_post_date": None,
                "pending_approval": None,
                "status": "not_started"
            })
    
    def _read_json(self, file_path: Path) -> Dict:
        """Read JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _write_json(self, file_path: Path, data: Dict):
        """Write JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ==================== Curriculum Methods ====================
    
    def get_curriculum(self) -> Dict:
        """Load the full curriculum."""
        return self._read_json(CURRICULUM_FILE)
    
    def get_topic_for_day(self, day: int) -> Optional[Dict]:
        """Get the topic information for a specific day."""
        curriculum = self.get_curriculum()
        for item in curriculum.get("curriculum", []):
            if item["day"] == day:
                return item
        return None
    
    def get_all_topics(self) -> List[Dict]:
        """Get all topics from curriculum."""
        curriculum = self.get_curriculum()
        return curriculum.get("curriculum", [])
    
    # ==================== History Methods ====================
    
    def get_history(self) -> Dict:
        """Get posting history."""
        return self._read_json(HISTORY_FILE)
    
    def add_to_history(self, day: int, topic: str, content: str, 
                       linkedin_post_id: Optional[str] = None):
        """Add a posted item to history."""
        history = self.get_history()
        
        posted_item = {
            "day": day,
            "topic": topic,
            "content": content,
            "linkedin_post_id": linkedin_post_id,
            "posted_at": datetime.now().isoformat(),
            "char_count": len(content)
        }
        
        history["posted_items"].append(posted_item)
        history["last_updated"] = datetime.now().isoformat()
        history["total_posts"] = len(history["posted_items"])
        
        self._write_json(HISTORY_FILE, history)
    
    def get_posted_days(self) -> List[int]:
        """Get list of days that have been posted."""
        history = self.get_history()
        return [item["day"] for item in history.get("posted_items", [])]
    
    def is_day_posted(self, day: int) -> bool:
        """Check if a specific day has been posted."""
        return day in self.get_posted_days()
    
    def get_recent_posts(self, count: int = 5) -> List[Dict]:
        """Get the most recent posts for context."""
        history = self.get_history()
        posted_items = history.get("posted_items", [])
        return posted_items[-count:] if posted_items else []
    
    def get_recent_posts_summary(self, count: int = 3) -> str:
        """Get a summary of recent posts for continuity."""
        recent = self.get_recent_posts(count)
        if not recent:
            return "This is the beginning of the 90-day AI journey!"
        
        summary_parts = []
        for post in recent:
            summary_parts.append(f"- Day {post['day']}: {post['topic']}")
        
        return "Recent posts in this series:\n" + "\n".join(summary_parts)
    
    # ==================== State Methods ====================
    
    def get_state(self) -> Dict:
        """Get current agent state."""
        return self._read_json(STATE_FILE)
    
    def update_state(self, **kwargs):
        """Update agent state with provided key-value pairs."""
        state = self.get_state()
        state.update(kwargs)
        self._write_json(STATE_FILE, state)
    
    def get_current_day(self) -> int:
        """Get the current day in the 90-day journey."""
        state = self.get_state()
        return state.get("current_day", 1)
    
    def increment_day(self):
        """Move to the next day."""
        current = self.get_current_day()
        if current < 90:
            self.update_state(current_day=current + 1)
    
    def set_pending_approval(self, content: Dict):
        """Set content pending approval."""
        self.update_state(
            pending_approval=content,
            status="pending_approval"
        )
    
    def clear_pending_approval(self):
        """Clear pending approval content."""
        self.update_state(
            pending_approval=None,
            status="active"
        )
    
    def get_pending_approval(self) -> Optional[Dict]:
        """Get content pending approval."""
        state = self.get_state()
        return state.get("pending_approval")
    
    def start_journey(self):
        """Initialize the 90-day journey."""
        self.update_state(
            current_day=1,
            started_at=datetime.now().isoformat(),
            status="active"
        )
    
    def mark_post_completed(self, day: int):
        """Mark a day's post as completed."""
        self.update_state(
            last_post_date=datetime.now().isoformat()
        )
        self.increment_day()
    
    def get_progress(self) -> Dict:
        """Get overall progress statistics."""
        state = self.get_state()
        history = self.get_history()
        
        return {
            "current_day": state.get("current_day", 1),
            "total_posts": history.get("total_posts", 0),
            "started_at": state.get("started_at"),
            "last_post_date": state.get("last_post_date"),
            "status": state.get("status", "not_started"),
            "completion_percentage": round((history.get("total_posts", 0) / 90) * 100, 1)
        }
    
    def reset_journey(self):
        """Reset the entire journey (use with caution)."""
        self._write_json(STATE_FILE, {
            "current_day": 1,
            "started_at": None,
            "last_post_date": None,
            "pending_approval": None,
            "status": "not_started"
        })
        self._write_json(HISTORY_FILE, {
            "posted_items": [],
            "last_updated": None,
            "total_posts": 0
        })
