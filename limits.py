from db import get_daily_uses, increment_daily_uses

DAILY_LIMIT = 5


def check_and_increment_limit(email: str) -> tuple[bool, int]:
    """
    Returns: (can_use, remaining_after_use)
    """
    uses = get_daily_uses(email)
    remaining = DAILY_LIMIT - uses

    if remaining <= 0:
        return False, 0

    increment_daily_uses(email)
    return True, remaining - 1


def get_remaining(email: str) -> int:
    uses = get_daily_uses(email)
    return max(0, DAILY_LIMIT - uses)
