import re
from dataclasses import dataclass

_INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|your|prior)\s+instructions?",
    r"you\s+are\s+now\s+",
    r"act\s+as\s+(a\s+)?(?!procurement|vendor|assistant)",
    r"pretend\s+(you\s+are|to\s+be)",
    r"(jailbreak|dan\s+mode|developer\s+mode|god\s+mode)",
    r"disregard\s+(your|all|previous)\s+(instructions?|rules?|guidelines?)",
    r"forget\s+(everything|all\s+previous|your\s+instructions?)",
    r"new\s+persona",
    r"(system\s+prompt|your\s+prompt)\s*[:=]",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

_MAX_REPEATED_CHARS = 50  # "aaaaaaa..." spam


@dataclass
class GuardResult:
    allowed: bool
    reply: str | None = None  # set when blocked


def check(message: str) -> GuardResult:
    """
    Screen a chat message before it reaches LangGraph.
    Returns GuardResult(allowed=True) if message is safe.
    Returns GuardResult(allowed=False, reply=...) with a safe reply if blocked.
    """
    for pattern in _COMPILED:
        if pattern.search(message):
            return GuardResult(
                allowed=False,
                reply="I can only help with procurement and vendor selection questions.",
            )

    if _has_repeated_spam(message):
        return GuardResult(
            allowed=False,
            reply="Your message looks like spam. Please describe what you need.",
        )

    return GuardResult(allowed=True)


def _has_repeated_spam(message: str) -> bool:
    return bool(re.search(rf"(.)\1{{{_MAX_REPEATED_CHARS},}}", message))
