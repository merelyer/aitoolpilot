#!/usr/bin/env python3
"""
AI Income Automation - Scheduler
Runs the content generation pipeline on a schedule.
Can be run via cron, systemd timer, or as a long-running daemon.
"""

import os
import sys
import json
import time
import signal
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.content_engine import ContentEngine


class ContentScheduler:
    """Scheduler that runs content generation on a recurring schedule."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = ROOT / "config" / "settings.json"
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.frequency_hours = self.config["schedule"]["frequency_hours"]
        self.running = False
        self.run_count = 0
        self.max_posts = self.config["site"]["max_posts_total"]
        self.state_file = ROOT / "data" / "scheduler_state.json"
        self.engine = ContentEngine(config_path=config_path)

        # Load previous state
        self.state = self._load_state()

    def _load_state(self) -> dict:
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "started_at": None,
            "total_runs": 0,
            "total_posts": 0,
            "total_errors": 0,
            "last_run_at": None,
            "next_run_at": None,
            "categories_processed": [],
        }

    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, default=str)

    def run_once(self) -> dict:
        """Execute one content generation run."""
        print(f"\n{'='*60}")
        print(f"⏰ Scheduled Run #{self.run_count + 1}")
        print(f"   Time: {datetime.now(timezone.utc).isoformat()}")
        print(f"   Total posts so far: {self.state['total_posts']}")
        print(f"{'='*60}")

        try:
            # Rotate through categories
            categories = self.config["seo"]["categories"]
            cat_idx = self.run_count % len(categories)
            category = categories[cat_idx]

            print(f"📂 Processing category: {category}")

            posts = self.engine.run_auto(category=category)

            self.run_count += 1
            self.state["total_runs"] += 1
            self.state["total_posts"] += len(posts)
            self.state["last_run_at"] = datetime.now(timezone.utc).isoformat()
            self.state["categories_processed"].append(category)
            self._save_state()

            result = {
                "success": True,
                "posts_generated": len(posts),
                "category": category,
                "total_posts": self.state["total_posts"],
            }
            print(f"✅ Run complete: {len(posts)} posts generated")
            return result

        except Exception as e:
            self.state["total_errors"] += 1
            self._save_state()
            print(f"❌ Run failed: {e}")
            return {"success": False, "error": str(e)}

    def run_daemon(self):
        """Run as a long-lived daemon process."""
        self.running = True
        self.state["started_at"] = datetime.now(timezone.utc).isoformat()
        self._save_state()

        print(f"""
╔══════════════════════════════════════════════════════════╗
║       🤖 AI INCOME AUTOMATION - DAEMON STARTED          ║
╠══════════════════════════════════════════════════════════╣
║  Frequency:  Every {self.frequency_hours} hours                      ║
║  Max posts:  {self.max_posts} total                              ║
║  Started:    {self.state['started_at']}  ║
╚══════════════════════════════════════════════════════════╝
""")

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        # Run immediately on start
        self.run_once()

        while self.running:
            # Check if we've reached the maximum posts
            if self.state["total_posts"] >= self.max_posts:
                print(f"\n🎉 Reached maximum post count ({self.max_posts}). Stopping daemon.")
                self.running = False
                break

            sleep_seconds = self.frequency_hours * 3600
            next_run = datetime.now(timezone.utc).timestamp() + sleep_seconds
            self.state["next_run_at"] = datetime.fromtimestamp(next_run, tz=timezone.utc).isoformat()
            self._save_state()

            print(f"\n💤 Sleeping for {self.frequency_hours} hours...")
            print(f"   Next run: {self.state['next_run_at']}")

            # Sleep in 60-second increments so we can handle shutdown
            for _ in range(int(sleep_seconds / 60)):
                if not self.running:
                    break
                time.sleep(60)

            if self.running:
                self.run_once()

        self._handle_shutdown(None, None)

    def _handle_shutdown(self, signum, frame):
        """Graceful shutdown."""
        print(f"\n🛑 Shutting down scheduler...")
        print(f"   Total runs: {self.state['total_runs']}")
        print(f"   Total posts: {self.state['total_posts']}")
        print(f"   Total errors: {self.state['total_errors']}")
        self.running = False
        self._save_state()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Income Automation - Scheduler")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (continuous)")
    parser.add_argument("--config", type=str, default=None, help="Path to config file")
    args = parser.parse_args()

    scheduler = ContentScheduler(
        config_path=Path(args.config) if args.config else None
    )

    if args.once:
        result = scheduler.run_once()
        print(f"\nResult: {json.dumps(result, indent=2, default=str)}")
    elif args.daemon:
        scheduler.run_daemon()
    else:
        # Default: run once
        result = scheduler.run_once()
        print(f"\nResult: {json.dumps(result, indent=2, default=str)}")


if __name__ == "__main__":
    main()
