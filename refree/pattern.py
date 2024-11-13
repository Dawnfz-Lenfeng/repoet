import re
from typing import Iterator, Match, Optional, Union


class Pattern:
    """A wrapper class for compiled regular expressions"""

    def __init__(self, pattern: str):
        self._pattern = pattern
        self._compiled = None  # lazy compilation

    def __str__(self) -> str:
        return self._pattern

    @property
    def pattern(self) -> str:
        """Return the pattern string"""
        return self._pattern

    @property
    def compiled(self):
        """Lazy compilation of the pattern"""
        if self._compiled is None:
            self._compiled = re.compile(self._pattern)
        return self._compiled

    @property
    def groups(self) -> int:
        """Return number of capturing groups"""
        return self.compiled.groups

    @property
    def groupindex(self) -> dict[str, int]:
        """Return dictionary of named capturing groups"""
        return self.compiled.groupindex

    def match(self, string: str, pos: int = 0, endpos: int = None) -> Optional[Match]:
        """Match pattern at start of string"""
        if endpos is None:
            return self.compiled.match(string, pos)
        return self.compiled.match(string, pos, endpos)

    def search(self, string: str, pos: int = 0, endpos: int = None) -> Optional[Match]:
        """Search pattern anywhere in string"""
        if endpos is None:
            return self.compiled.search(string, pos)
        return self.compiled.search(string, pos, endpos)

    def findall(self, string: str) -> list[str]:
        """Find all non-overlapping matches in string"""
        return self.compiled.findall(string)

    def finditer(self, string: str) -> Iterator[Match]:
        """Return iterator over all non-overlapping matches"""
        return self.compiled.finditer(string)

    def split(self, string: str, maxsplit: int = 0) -> list[str]:
        """Split string by pattern"""
        return self.compiled.split(string, maxsplit)

    def sub(self, repl: Union[str, callable], string: str, count: int = 0) -> str:
        """Replace matches with replacement string"""
        return self.compiled.sub(repl, string, count)

    def subn(
        self, repl: Union[str, callable], string: str, count: int = 0
    ) -> tuple[str, int]:
        """Replace matches and return tuple (new_string, number_of_subs_made)"""
        return self.compiled.subn(repl, string, count)

    def __radd__(self, other: str) -> "Pattern":
        """Handle string + Pattern"""
        return Pattern(re.escape(other) + self._pattern)

    def __add__(self, other: Union["Pattern", str]) -> "Pattern":
        """Implement + operator for sequence concatenation"""
        if isinstance(other, Pattern):
            return Pattern(f"{self._pattern}{other._pattern}")
        return Pattern(f"{self._pattern}{re.escape(other)}")

    def __or__(self, other: Union["Pattern", str]) -> "Pattern":
        """Implement | operator for alternatives"""
        other_pattern = other._pattern if isinstance(other, Pattern) else re.escape(other)
        return Pattern(f"(?:{self._pattern}|{other_pattern})")

    def __mul__(self, n: int) -> "Pattern":
        """Implement * operator for repetition
        Example: pattern * 3 equals times(3)(pattern)
        """
        return Pattern(f"(?:{self._pattern}{{{n}}})")
