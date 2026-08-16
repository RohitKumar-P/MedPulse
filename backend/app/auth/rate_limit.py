import time
from collections import defaultdict, deque
from threading import Lock


LOGIN_LIMIT = 10
REGISTER_LIMIT = 5

WINDOW_SECONDS = 60


_requests = defaultdict(deque)
_lock = Lock()


def allow_request(
    key: str,
    limit: int
) -> bool:

    now = time.monotonic()

    with _lock:

        timestamps = _requests[key]

        while (
            timestamps
            and now - timestamps[0] > WINDOW_SECONDS
        ):
            timestamps.popleft()

        if len(timestamps) >= limit:
            return False

        timestamps.append(now)

        return True


def clear_rate_limits():

    with _lock:
        _requests.clear()
