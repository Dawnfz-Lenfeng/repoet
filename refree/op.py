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


def group(p: Pattern, name: Optional[str] = None) -> Pattern:
    """Capture group, optionally named
    
    Examples:
        group(word)              -> (\\w+)
        group(word, "username")  -> (?P<username>\\w+)
    """
    if name is not None:
        return Pattern(f"(?P<{name}>{p})")
    return Pattern(f"({p})")


# Character classes
def within(*cs: str) -> Pattern:
    """Character class [...] - match any single character within the specified set
    
    Examples:
        within("0-9")     -> [0-9]
        within("aeiou")   -> [aeiou]
        within("a-zA-Z")  -> [a-zA-Z]
    """
    return Pattern(f"[{''.join(cs)}]")


def exclude(*cs: str) -> Pattern:
    """Negated character class [^...] - match any single character excluding those in the specified set
    
    Examples:
        exclude("0-9")    -> [^0-9]
        exclude("aeiou")  -> [^aeiou]
        exclude("a-zA-Z") -> [^a-zA-Z]
    """
    return Pattern(f"[^{''.join(cs)}]")


# Common patterns
digit = Pattern(r"\d")
letter = Pattern(pattern=r"\w")
word = Pattern(r"\w+")
space = Pattern(r"\s")
any = Pattern(".")


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


# Assertions
begin = Pattern("^")  # Start of string
end = Pattern("$")  # End of string
