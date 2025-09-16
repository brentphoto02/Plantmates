from enum import Enum


class TransactionType(str, Enum):
    """Supported listing transaction configurations."""

    swap = "swap"
    sale = "sale"
    free = "free"


class MatchStatus(str, Enum):
    """Match lifecycle stages."""

    liked = "liked"
    passed = "passed"
    matched = "matched"


class ThreadStatus(str, Enum):
    """Conversation lifecycle states."""

    active = "active"
    archived = "archived"


class SwapStatus(str, Enum):
    """Swap lifecycle states for marketplace transactions."""

    pending = "pending"
    agreed = "agreed"
    completed = "completed"
    canceled = "canceled"
    no_show = "no_show"
