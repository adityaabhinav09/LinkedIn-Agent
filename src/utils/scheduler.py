"""Scheduler for managing daily posting times."""

import schedule
import time
from datetime import datetime, timedelta
from typing import Callable, Optional
import threading
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import POSTING_TIME, TIMEZONE


class Scheduler:
    """Manages scheduling for the daily posting routine."""
    
    def __init__(self, posting_time: str = POSTING_TIME):
        """
        Initialize scheduler.
        
        Args:
            posting_time: Time to trigger daily post (HH:MM format)
        """
        self.posting_time = posting_time
        self.job = None
        self._stop_event = threading.Event()
        self._thread = None
    
    def schedule_daily(self, callback: Callable):
        """
        Schedule a daily callback at the specified time.
        
        Args:
            callback: Function to call at scheduled time
        """
        self.job = schedule.every().day.at(self.posting_time).do(callback)
        print(f"📅 Scheduled daily post at {self.posting_time}")
    
    def start(self):
        """Start the scheduler in a background thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("🚀 Scheduler started")
    
    def _run(self):
        """Internal run loop for scheduler."""
        while not self._stop_event.is_set():
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop the scheduler."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        schedule.clear()
        print("🛑 Scheduler stopped")
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Get the next scheduled run time."""
        if self.job:
            return self.job.next_run
        return None
    
    def time_until_next_run(self) -> Optional[timedelta]:
        """Get time remaining until next run."""
        next_run = self.get_next_run_time()
        if next_run:
            return next_run - datetime.now()
        return None
    
    def run_now(self, callback: Callable):
        """Run the callback immediately (for testing/manual trigger)."""
        print("⚡ Running immediately...")
        callback()
    
    def is_posting_time(self) -> bool:
        """Check if current time is within posting window."""
        now = datetime.now()
        scheduled_hour, scheduled_minute = map(int, self.posting_time.split(':'))
        
        # Allow 5-minute window around scheduled time
        scheduled_time = now.replace(hour=scheduled_hour, minute=scheduled_minute, second=0)
        time_diff = abs((now - scheduled_time).total_seconds())
        
        return time_diff <= 300  # 5 minutes window
    
    @staticmethod
    def format_time_remaining(td: timedelta) -> str:
        """Format timedelta for display."""
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class ManualTrigger:
    """Allows manual triggering of the posting workflow."""
    
    def __init__(self, callback: Callable):
        self.callback = callback
    
    def trigger(self):
        """Manually trigger the posting workflow."""
        print("\n🔔 Manual trigger activated!")
        self.callback()
