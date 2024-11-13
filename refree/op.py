import re
from typing import Optional, Union

from .pattern import Pattern


# Basic constructors
def lit(text: str) -> Pattern:
    """Literal text pattern"""
    return Pattern(re.escape(text))


def seq(*patterns: Union[Pattern, str]) -> Pattern:
    """Sequence of patterns"""
    return Pattern("".join(str(p) for p in patterns))


def alt(*patterns: Union[Pattern, str]) -> Pattern:
    """Alternative patterns (OR)"""
    return Pattern(f"(?:{'|'.join(str(p) for p in patterns)})")


# Quantifiers
def times(n: int) -> Pattern:
    """Repeat exactly n times"""
    return lambda p: Pattern(f"(?:{p}){{{n}}}")


def between(min_n: int, max_n: Optional[int] = None) -> Pattern:
    """Repeat between min_n and max_n times"""
    max_str = str(max_n) if max_n is not None else ""
    return lambda p: Pattern(f"(?:{p}){{{min_n},{max_str}}}")


def many(p: Pattern) -> Pattern:
    """Zero or more times (*)"""
    return Pattern(f"(?:{p})*")


def some(p: Pattern) -> Pattern:
    """One or more times (+)"""
    return Pattern(f"(?:{p})+")


def maybe(p: Pattern) -> Pattern:
    """Zero or one time (?)"""
    return Pattern(f"(?:{p})?")


# Groups
def group(p: Pattern) -> Pattern:
    """Capture group"""
    return Pattern(f"({p})")


# Character classes
digit = Pattern(r"\d")
word = Pattern(r"\w")
space = Pattern(r"\s")
any_char = Pattern(".")


def chars(*cs: str) -> Pattern:
    """Character class [...]"""
    return Pattern(f"[{''.join(cs)}]")


# Assertions
begin = Pattern("^")  # Start of string
end = Pattern("$")  # End of string
