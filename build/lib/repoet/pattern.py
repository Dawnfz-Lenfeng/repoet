import re
from typing import Union


def re_escape(fn):
    def arg_escaped(this, *args):
        t = [re.escape(arg) if isinstance(arg, str) else arg for arg in args]
        return fn(this, *t)

    return arg_escaped


class Pattern:
    """A wrapper class for compiled regular expressions"""

    def __init__(self, pattern: str):
        self._pattern = pattern
        self._regex = None

    def __str__(self) -> str:
        return self._pattern

    def __getattr__(self, attr):
        if self._regex is None:
            self._regex = re.compile(self._pattern)
        return getattr(self._regex, attr)

    @re_escape
    def __radd__(self, other: str) -> "Pattern":
        return Pattern(other + self._pattern)

    @re_escape
    def __add__(self, other: Union["Pattern", str]) -> "Pattern":
        return Pattern(f"{self._pattern}{other}")

    @re_escape
    def __or__(self, other: Union["Pattern", str]) -> "Pattern":
        return Pattern(f"(?:{self._pattern}|{other})")

    def __mul__(self, n: int) -> "Pattern":
        return Pattern(f"(?:{self._pattern}{{{n}}})")
