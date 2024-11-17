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

    def __getitem__(self, key) -> "Pattern":
        """Use indexing for quantifiers

        pattern[n]     -> Exactly n times {n}
        pattern[n:]    -> n or more times {n,}
        pattern[:n]    -> Up to n times {,n}
        pattern[m:n]   -> Between m and n times {m,n}
        pattern[:]     -> Zero or more times (*)
        pattern[1:]    -> One or more times (+)
        pattern[0:1]   -> Zero or one time (?)
        """
        if isinstance(key, slice):
            start, stop = key.start, key.stop
            if start is None and stop is None:  # [:]
                return Pattern(f"(?:{self})*")
            elif start == 1 and stop is None:  # [1:]
                return Pattern(f"(?:{self})+")
            elif start == 0 and stop == 1:  # [0:1]
                return Pattern(f"(?:{self})?")
            else:  # [m:n]
                start_str = str(start) if start is not None else ""
                stop_str = str(stop) if stop is not None else ""
                return Pattern(f"(?:{self}){{{start_str},{stop_str}}}")
        else:  # [n]
            return Pattern(f"(?:{self}){{{key}}}")
