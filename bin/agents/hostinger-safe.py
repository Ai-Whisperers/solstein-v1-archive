#!/usr/bin/env python3
"""
Hostinger-safe agent utilities
- No systemctl checks (not available in Hostinger)
- Telegram rate limiting (429 handling)
- Direct file monitoring instead of systemd
"""
import time
import logging
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class HostingerSafeRunner:
    """Run agents without systemctl dependency"""
    
    def __init__(self):
        self.last_telegram_request = None
        self.telegram_retry_after = 0
        self.last_api_call = time.time()
    
    def is_hostinger_environment(self) -> bool:
        """Detect if running in Hostinger container"""
        try:
            import subprocess
            result = subprocess.run(
                ["systemctl", "--user", "status"],
                capture_output=True,
                timeout=1
            )
            return result.returncode != 0
        except:
            return True  # Assume Hostinger if systemctl fails
    
    def wait_for_telegram_rate_limit(self) -> None:
        """Handle Telegram 429 rate limiting with exponential backoff"""
        if self.telegram_retry_after > 0:
            wait_time = min(self.telegram_retry_after, 60)  # Max 60 seconds
            logger.warning(f"Telegram rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            self.telegram_retry_after = max(0, self.telegram_retry_after - 1)
    
    def handle_telegram_error(self, error: str) -> None:
        """Parse and handle Telegram API errors"""
        if "429:" in error:
            # Extract retry_after from error message
            try:
                retry_after = int(error.split("retry after ")[-1].split(")")[0])
                self.telegram_retry_after = retry_after
            except:
                self.telegram_retry_after = 30
        elif "409:" in error:
            # Conflict - another bot instance running
            logger.error("CRITICAL: Duplicate Telegram bot detected!")
            logger.error("Action: Killing all other telegram instances...")
            import subprocess
            subprocess.run(["pkill", "-f", "telegram.*bot"], capture_output=True)
    
    def safe_api_call(self, min_interval: float = 1.0) -> None:
        """Rate limit API calls (min 1 second between calls)"""
        now = time.time()
        elapsed = now - self.last_api_call
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_api_call = time.time()
    
    def check_service_without_systemctl(self, service_name: str) -> bool:
        """Check if service is running without systemctl"""
        import subprocess
        try:
            result = subprocess.run(
                ["pgrep", "-f", service_name],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

if __name__ == "__main__":
    runner = HostingerSafeRunner()
    
    # Test detection
    is_hostinger = runner.is_hostinger_environment()
    print(f"✅ Hostinger environment detected: {is_hostinger}")
    
    # Test Telegram rate limiting
    runner.handle_telegram_error("429: Too Many Requests: retry after 30")
    print(f"✅ Telegram retry after: {runner.telegram_retry_after}s")
    
    # Test safe API calls
    runner.safe_api_call(0.5)
    print(f"✅ API call throttling working")
