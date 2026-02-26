#!/usr/bin/env python3
"""Rate limiting and caching to avoid Hostinger API throttling"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

class RateLimiter:
    def __init__(self, cache_dir="/home/ai-whisperers/solstein/.cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = 300  # 5 minutes
        
    def get_cached(self, key):
        """Get cached result if still valid"""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
            
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                print(f"[CACHE HIT] {key}")
                return data['result']
        
        return None
    
    def set_cached(self, key, result):
        """Cache result with timestamp"""
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'result': result
            }, f)
    
    def wait_if_needed(self, api_name, min_interval=2):
        """Add delay between API calls"""
        print(f"[RATE LIMIT] Waiting {min_interval}s before {api_name}")
        time.sleep(min_interval)

if __name__ == "__main__":
    limiter = RateLimiter()
    
    # Test caching
    result = limiter.get_cached("test_key")
    if result:
        print(f"Found cached result: {result}")
    else:
        limiter.set_cached("test_key", {"status": "ok"})
        print("Cached new result")
    
    # Check again
    result = limiter.get_cached("test_key")
    print(f"Retrieved from cache: {result}")
