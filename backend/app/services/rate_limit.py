import logging
import threading
import time

from fastapi import Request
from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings
from app.core.request_meta import extract_client_ip

logger = logging.getLogger(__name__)

_WINDOW_SECONDS = {
    "second": 1,
    "seconds": 1,
    "minute": 60,
    "minutes": 60,
    "hour": 3600,
    "hours": 3600,
    "day": 86400,
    "days": 86400,
}


class RateLimitExceededError(Exception):
    pass


def _parse_limit(limit_value: str) -> tuple[int, int]:
    if not limit_value or "/" not in limit_value:
        raise ValueError(f"Invalid rate limit value: {limit_value!r}")

    count_raw, window_raw = [part.strip().lower() for part in limit_value.split("/", maxsplit=1)]
    max_requests = int(count_raw)
    window_seconds = _WINDOW_SECONDS.get(window_raw)
    if not window_seconds or max_requests <= 0:
        raise ValueError(f"Invalid rate limit value: {limit_value!r}")

    return max_requests, window_seconds


class RateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._memory_state: dict[str, tuple[int, float]] = {}
        self._redis_client: Redis | None = None
        self._redis_url: str | None = None

    def reset_state(self) -> None:
        with self._lock:
            self._memory_state.clear()
            self._redis_client = None
            self._redis_url = None

    def _get_redis_client(self, redis_url: str | None) -> Redis | None:
        if not redis_url:
            return None

        with self._lock:
            if self._redis_client is None or self._redis_url != redis_url:
                self._redis_client = Redis.from_url(redis_url, decode_responses=True, socket_timeout=1.0)
                self._redis_url = redis_url
            return self._redis_client

    def _enforce_in_memory(self, key: str, max_requests: int, window_seconds: int) -> None:
        now = time.time()
        expires_at = now + window_seconds

        with self._lock:
            current_count, current_expiry = self._memory_state.get(key, (0, expires_at))
            if current_expiry <= now:
                current_count = 0
                current_expiry = expires_at

            current_count += 1
            self._memory_state[key] = (current_count, current_expiry)

        if current_count > max_requests:
            raise RateLimitExceededError

    def _enforce_with_redis(self, key: str, max_requests: int, window_seconds: int, redis_url: str | None) -> None:
        redis_client = self._get_redis_client(redis_url)
        if redis_client is None:
            self._enforce_in_memory(key, max_requests, window_seconds)
            return

        try:
            with redis_client.pipeline() as pipeline:
                pipeline.incr(key)
                pipeline.expire(key, window_seconds + 1)
                incremented, _ = pipeline.execute()
            if int(incremented) > max_requests:
                raise RateLimitExceededError
        except RedisError:
            logger.exception("Redis unavailable for rate limiting; falling back to in-memory limiting.")
            self._enforce_in_memory(key, max_requests, window_seconds)

    def enforce(self, request: Request, endpoint_name: str, limit_value: str) -> None:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return

        max_requests, window_seconds = _parse_limit(limit_value)
        client_ip = extract_client_ip(request) or "unknown"
        bucket = int(time.time() // window_seconds)
        key = f"rate_limit:{endpoint_name}:{client_ip}:{bucket}"
        self._enforce_with_redis(key, max_requests, window_seconds, settings.redis_url)


_rate_limiter = RateLimiter()


def enforce_rate_limit(request: Request, endpoint_name: str, limit_value: str) -> None:
    _rate_limiter.enforce(request, endpoint_name, limit_value)


def reset_rate_limiter_state() -> None:
    _rate_limiter.reset_state()
