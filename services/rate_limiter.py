"""
Centralized Gemini API Rate Limiter.

Uses a sliding window approach to enforce RPM (requests per minute) and
RPD (requests per day) limits. Thread-safe — shared across the trend
processing (llm_service) and the content pipeline (pipeline/gemini_client).

Both modules call `rate_limiter.wait_for_slot()` BEFORE making any API call.
If the limit would be exceeded, the call blocks until a slot opens.

Default limits are conservative (well below typical free-tier caps) to
prevent 429 errors. Adjust via environment variables:
  GEMINI_RPM=10        (default: 10 requests per minute)
  GEMINI_RPD=1400      (default: 1400 requests per day)
"""

import os
import time
import threading

class GeminiRateLimiter:
    """
    Simplified rate limiter that spaces out requests evenly to avoid hitting
    the 15 RPM limit on the free tier, and thus avoids huge 60-second waits.
    """

    def __init__(self, rpm: int = None, rpd: int = None):
        # 15 RPM means 1 request every 4 seconds. 
        # We enforce a strict delay between requests.
        self.rpm = rpm or int(os.getenv("GEMINI_RPM", "15"))
        self.min_spacing = 60.0 / self.rpm
        
        self._lock = threading.Lock()
        self._last_request_time = 0.0

        print(f"[RateLimiter] Initialized — Spacing requests by {self.min_spacing:.1f}s")

    def wait_for_slot(self) -> float:
        """
        Blocks until enough time has passed since the last request.
        Returns the number of seconds waited.
        """
        waited = 0.0
        with self._lock:
            now = time.time()
            time_since_last = now - self._last_request_time
            
            if time_since_last < self.min_spacing:
                wait_time = self.min_spacing - time_since_last
                time.sleep(wait_time)
                waited = wait_time
                self._last_request_time = now + wait_time
            else:
                self._last_request_time = now

        return waited

    def record_request(self):
        """Manually record a request."""
        with self._lock:
            self._last_request_time = time.time()

    def get_usage(self) -> dict:
        """Returns dummy usage stats since we use spacing now."""
        return {
            "rpm_used": 1,
            "rpm_limit": self.rpm,
            "rpd_used": 1,
            "rpd_limit": 1500,
        }

# ── Singleton instance shared across the entire app ──
_limiter = None
_init_lock = threading.Lock()

def get_limiter() -> GeminiRateLimiter:
    global _limiter
    if _limiter is None:
        with _init_lock:
            if _limiter is None:
                _limiter = GeminiRateLimiter()
    return _limiter

def wait_for_slot() -> float:
    return get_limiter().wait_for_slot()

def get_usage() -> dict:
    return get_limiter().get_usage()
