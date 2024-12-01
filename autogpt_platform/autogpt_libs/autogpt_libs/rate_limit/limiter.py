import time
import redis
from typing import Tuple
from .config import RATE_LIMIT_SETTINGS


class RateLimiter:
    def __init__(self, redis_url: str = RATE_LIMIT_SETTINGS.redis_url,
                 requests_per_minute: int = RATE_LIMIT_SETTINGS.requests_per_minute):
        self.redis = redis.from_url(redis_url)
        self.window = 60
        self.max_requests = requests_per_minute

    async def check_rate_limit(self, api_key_id: str) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limits.

        Args:
            api_key_id: The API key identifier to check

        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time)
        """
        now = time.time()
        window_start = now - self.window
        key = f"ratelimit:{api_key_id}:1min"

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcount(key, window_start, now)
        pipe.expire(key, self.window)

        _, _, request_count, _ = pipe.execute()

        remaining = max(0, self.max_requests - request_count)
        reset_time = int(now + self.window)

        return request_count <= self.max_requests, remaining, reset_time
