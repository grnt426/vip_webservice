import time
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TokenBucketRateLimiter:
    def __init__(self, bucket_size: int = 300, refill_rate: float = 5.0):
        self.bucket_size = bucket_size
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = bucket_size
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
        logger.info(f"Initialized rate limiter with bucket size {bucket_size} and refill rate {refill_rate}/s")

    async def _refill(self) -> None:
        """Refill tokens based on time elapsed"""
        now = time.monotonic()
        elapsed = now - self.last_refill
        refill = elapsed * self.refill_rate
        self.tokens = min(self.bucket_size, self.tokens + refill)
        self.last_refill = now
        logger.debug(f"Refilled tokens. Current tokens: {self.tokens:.2f}")

    async def acquire(self, tokens: int = 1) -> None:
        """Acquire tokens, waiting if necessary"""
        async with self._lock:
            await self._refill()
            
            if tokens > self.bucket_size:
                raise ValueError(f"Requested tokens ({tokens}) exceeds bucket size ({self.bucket_size})")

            # If we don't have enough tokens, calculate wait time
            if self.tokens < tokens:
                needed = tokens - self.tokens
                wait_time = needed / self.refill_rate
                logger.info(f"Rate limit reached. Waiting {wait_time:.2f}s for {needed:.2f} tokens")
                await asyncio.sleep(wait_time)
                await self._refill()  # Refill after waiting

            self.tokens -= tokens
            logger.debug(f"Acquired {tokens} tokens. Remaining: {self.tokens:.2f}")

    @property
    def available_tokens(self) -> float:
        """Get current number of available tokens (for monitoring)"""
        return self.tokens 