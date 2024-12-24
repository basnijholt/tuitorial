"""Highlighting utilities for the tutorial."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from re import Pattern

from rich.style import Style


class FocusType(Enum):
    """Types of focus patterns."""

    LITERAL = auto()
    REGEX = auto()
    LINE = auto()
    RANGE = auto()
    STARTSWITH = auto()


@dataclass
class Focus:
    """A pattern to focus on with its style."""

    pattern: str | Pattern | tuple[int, int] | int | tuple[str, bool]
    style: Style = Style(color="yellow", bold=True)  # noqa: RUF009
    type: FocusType = FocusType.LITERAL

    @classmethod
    def literal(
        cls,
        text: str,
        style: Style = Style(color="yellow", bold=True),  # noqa: B008
        *,
        word_boundary: bool = False,
    ) -> Focus:
        """Create a focus for a literal string.

        Parameters
        ----------
        text
            The text to match
        style
            The style to apply to the matched text
        word_boundary
            If True, only match the text when it appears as a word

        """
        if word_boundary:
            pattern = re.compile(rf"\b{re.escape(text)}\b")
            return cls(pattern, style, FocusType.REGEX)
        return cls(text, style, FocusType.LITERAL)

    @classmethod
    def regex(
        cls,
        pattern: str | Pattern,
        style: Style = Style(color="green", bold=True),  # noqa: B008
    ) -> Focus:
        """Create a focus for a regular expression."""
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return cls(pattern, style, FocusType.REGEX)

    @classmethod
    def line(
        cls,
        line_number: int,
        style: Style = Style(color="cyan", bold=True),  # noqa: B008
    ) -> Focus:
        """Create a focus for a line number."""
        return cls(line_number, style, FocusType.LINE)

    @classmethod
    def range(
        cls,
        start: int,
        end: int,
        style: Style = Style(color="magenta", bold=True),  # noqa: B008
    ) -> Focus:
        """Create a focus for a range of characters."""
        return cls((start, end), style, FocusType.RANGE)

    @classmethod
    def startswith(
        cls,
        text: str,
        style: Style = Style(color="blue", bold=True),  # noqa: B008
        *,
        from_start_of_line: bool = False,
    ) -> Focus:
        """Create a focus for text that starts with the given pattern.

        Parameters
        ----------
        text
            The text to match at the start
        style
            The style to apply to the matched text
        from_start_of_line
            If True, only match at the start of lines, if False match anywhere

        """
        return cls((text, from_start_of_line), style, FocusType.STARTSWITH)
