import re
from typing import Optional, Union

from .pattern import Pattern


def re_escape(skip_chars=None):
    if callable(skip_chars):
        func = skip_chars
        skip_chars = ""
        return re_escape()(func)

    if skip_chars is None:
        skip_chars = ""

    def decorator(fn):
        def arg_escaped(*args, **kwargs):
            def escape_with_skip(arg):
                if not isinstance(arg, str):
                    return arg

                # Check for literal backslash before escaped chars
                parts = []
                i = 0
                while i < len(arg):
                    if arg[i] == "\\" and i + 1 < len(arg) and arg[i + 1] in skip_chars:
                        parts.append(arg[i : i + 2])  # Keep \char as is
                        i += 2
                    elif arg[i] in skip_chars:
                        parts.append(arg[i])
                        i += 1
                    else:
                        parts.append(re.escape(arg[i]))
                        i += 1
                return "".join(parts)

            escaped_args = [escape_with_skip(arg) for arg in args]
            return fn(*escaped_args, **kwargs)

        return arg_escaped

    return decorator


# Basic constructors
@re_escape
def lit(text: str) -> Pattern:
    """Literal text pattern - always escapes special characters"""
    return Pattern(text)


def regex(pattern: str) -> Pattern:
    """Raw regex pattern - no escaping applied"""
    return Pattern(pattern)


# Common patterns
digit = regex(r"\d")
nondigit = regex(r"\D")
letter = regex(r"\w")
nonletter = regex(r"\W")
word = regex(r"\w+")
space = regex(r"\s")
nonspace = regex(r"\S")
any = regex(".")
tab = regex("\t")
newline = regex("\n")

# Assertions
begin = regex("^")
end = regex("$")

# Boundary matchers
bound = regex(r"\b")
nonbound = regex(r"\B")


@re_escape
def seq(*patterns: Union[Pattern, str]) -> Pattern:
    """Sequence of patterns"""
    return Pattern("".join(map(str, patterns)))


@re_escape
def alt(*patterns: Union[Pattern, str]) -> Pattern:
    """Alternative patterns (OR)"""
    return Pattern(f"(?:{'|'.join(map(str, patterns))})")


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
@re_escape("-")
def anyof(*cs: str) -> Pattern:
    """Character class [...] - match any single character within the specified set"""
    return Pattern(f"[{''.join(map(str, cs))}]")


@re_escape("-")
def exclude(*cs: str) -> Pattern:
    """Negated character class [^...] - match any single character excluding those in the specified set"""
    return Pattern(f"[^{''.join(map(str, cs))}]")


# Quantifiers
@re_escape
def some(p: Pattern, greedy: bool = True) -> Pattern:
    """One or more times (+)

    Args:
        p: Pattern to repeat
        greedy: If True (default), use greedy matching; if False, use non-greedy matching

    Examples:
        some(word)           -> (?:\\w+)
        some(word, False)    -> (?:\\w+?)
    """
    return Pattern(f"(?:{p})+{'?' if not greedy else ''}")


@re_escape
def maybe(p: Pattern, greedy: bool = True) -> Pattern:
    """Zero or one time (?)

    Args:
        p: Pattern to make optional
        greedy: If True (default), use greedy matching; if False, use non-greedy matching
    """
    return Pattern(f"(?:{p})?{'?' if not greedy else ''}")


@re_escape
def mightsome(p: Pattern, greedy: bool = True) -> Pattern:
    """Zero or more times (*)

    Args:
        p: Pattern to repeat
        greedy: If True (default), use greedy matching; if False, use non-greedy matching
    """
    return Pattern(f"(?:{p})*{'?' if not greedy else ''}")


def times(n: int):
    """Repeat exactly n times"""

    @re_escape
    def repeat(p: Pattern) -> Pattern:
        return Pattern(f"(?:{p}){{{n}}}")

    return repeat


def between(min_n: int, max_n: Optional[int] = None, greedy: bool = True):
    """Repeat between min_n and max_n times

    Args:
        min_n: Minimum number of repetitions
        max_n: Maximum number of repetitions (if None, unlimited)
        greedy: If True (default), use greedy matching; if False, use non-greedy matching
    """
    max_str = str(max_n) if max_n is not None else ""

    @re_escape
    def repeat(p: Pattern) -> Pattern:
        return Pattern(f"(?:{p}){{{min_n},{max_str}}}{'?' if not greedy else ''}")

    return repeat


@re_escape
def ahead(*patterns: Union[Pattern, str]) -> Pattern:
    """Positive lookahead assertion (?=...)

    Examples:
        ahead("foo")  -> (?=foo)
        ahead(word)   -> (?=\\w+)
    """
    return Pattern(f"(?={''.join(map(str, patterns))})")


@re_escape
def not_ahead(*patterns: Union[Pattern, str]) -> Pattern:
    """Negative lookahead assertion (?!...)

    Examples:
        not_ahead("foo")  -> (?!foo)
    """
    return Pattern(f"(?!{''.join(map(str, patterns))})")


@re_escape
def behind(*patterns: Union[Pattern, str]) -> Pattern:
    """Positive lookbehind assertion (?<=...)

    Examples:
        behind("foo")  -> (?<=foo)
    """
    return Pattern(f"(?<={''.join(map(str, patterns))})")


@re_escape
def not_behind(*patterns: Union[Pattern, str]) -> Pattern:
    """Negative lookbehind assertion (?<!...)

    Examples:
        not_behind("foo")  -> (?<!foo)
    """
    return Pattern(f"(?<!{''.join(map(str, patterns))})")


@re_escape
def atomic_group(*patterns: Union[Pattern, str]) -> Pattern:
    """Create an atomic group (?>...)

    Examples:
        atomic_group("foo", word)  -> (?>foo\\w+)
    """
    return Pattern(f"(?>{''.join(map(str, patterns))})")
