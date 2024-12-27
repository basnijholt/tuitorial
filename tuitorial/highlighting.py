"""Highlighting utilities for the tutorial."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from re import Pattern
from typing import NamedTuple

from rich.style import Style


class FocusType(Enum):
    """Types of focus patterns."""

    LITERAL = auto()
    REGEX = auto()
    LINE = auto()
    RANGE = auto()
    STARTSWITH = auto()
    BETWEEN = auto()
    LINE_CONTAINING = auto()
    LINE_CONTAINING_REGEX = auto()
    SYNTAX = auto()
    MARKDOWN = auto()


@dataclass
class Focus:
    """A pattern to focus on with its style."""

    pattern: str | Pattern | _RangeTuple | int | _StartsWithTuple | _BetweenTuple
    style: Style = Style(color="yellow", bold=True)  # noqa: RUF009
    type: FocusType = FocusType.LITERAL
    extra: dict | None = None

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
        return cls(_RangeTuple(start, end), style, FocusType.RANGE)

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
        return cls(_StartsWithTuple(text, from_start_of_line), style, FocusType.STARTSWITH)

    @classmethod
    def between(
        cls,
        start_pattern: str,
        end_pattern: str,
        style: Style = Style(color="blue", bold=True),  # noqa: B008
        *,
        inclusive: bool = True,
        multiline: bool = True,
        match_index: int | None = None,  # Add this parameter
        greedy: bool = False,  # Add this parameter
    ) -> Focus:
        """Create a focus for text between two patterns.

        Parameters
        ----------
        start_pattern
            The pattern marking the start of the region
        end_pattern
            The pattern marking the end of the region
        style
            The style to apply to the matched text
        inclusive
            If True, include the start and end patterns in the highlighting
        multiline
            If True, match across multiple lines
        match_index
            If provided, only highlight the nth match (0-based).
            If None, highlight all matches.
        greedy
            If True, use greedy matching (matches longest possible string).
            If False, use non-greedy matching (matches shortest possible string).

        """
        return cls(
            _BetweenTuple(start_pattern, end_pattern, inclusive, multiline, match_index, greedy),
            style,
            FocusType.BETWEEN,
        )

    @classmethod
    def line_containing(
        cls,
        pattern: str,
        style: Style | str = Style(color="yellow", bold=True),  # noqa: B008
        *,
        lines_before: int = 0,
        lines_after: int = 0,
        regex: bool = False,
        match_index: int | None = None,
    ) -> Focus:
        """Select the entire line containing a pattern and optionally surrounding lines.

        Parameters
        ----------
        pattern
            The text pattern to search for.
        style
            The style to apply to the matched lines.
        lines_before
            Number of lines to include before the matched line.
        lines_after
            Number of lines to include after the matched line.
        regex
            If True, treat pattern as a regular expression.
        match_index
            If provided, only highlight the nth match (0-based).
            If None, highlight all matches.

        """
        if isinstance(style, str):
            style = Style.parse(style)

        return cls(
            pattern=pattern,
            style=style,
            type=FocusType.LINE_CONTAINING_REGEX if regex else FocusType.LINE_CONTAINING,
            extra={
                "lines_before": lines_before,
                "lines_after": lines_after,
                "match_index": match_index,
            },
        )

    @classmethod
    def syntax(
        cls,
        lexer: str = "python",
        *,
        theme: str | None = None,
        line_numbers: bool = False,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> Focus:
        """Use Rich's syntax highlighting.

        Parameters
        ----------
        lexer
            The language to use for syntax highlighting (default: "python")
        theme
            The color theme to use (default: None, uses terminal colors)
        line_numbers
            Whether to show line numbers
        start_line
            First line to highlight (0-based), if None highlight from start
        end_line
            Last line to highlight (0-based), if None highlight until end

        """
        return cls(
            pattern="",  # Not used
            style="",  # Not used
            type=FocusType.SYNTAX,
            extra={
                "lexer": lexer,
                "theme": theme,
                "line_numbers": line_numbers,
                "start_line": start_line,
                "end_line": end_line,
            },
        )

    @classmethod
    def markdown(cls) -> Focus:
        """Create a focus for a Markdown block."""
        return cls(
            pattern="",  # Not used
            style="",  # Not used
            type=FocusType.MARKDOWN,
        )

    def validate(self, focuses: list[Focus]) -> None:
        """Validate that there's at most one markdown or syntax focus."""
        if self.type == FocusType.MARKDOWN:
            if len([f for f in focuses if f.type == FocusType.MARKDOWN]) > 1:
                msg = "Only one markdown focus is allowed per step."
                raise ValueError(msg)
        elif self.type == FocusType.SYNTAX:  # noqa: SIM102
            if len([f for f in focuses if f.type == FocusType.SYNTAX]) > 1:
                msg = "Only one syntax focus is allowed per step."
                raise ValueError(msg)


class _BetweenTuple(NamedTuple):
    start_pattern: str
    end_pattern: str
    inclusive: bool
    multiline: bool
    match_index: int | None
    greedy: bool


class _StartsWithTuple(NamedTuple):
    text: str
    from_start_of_line: bool


class _RangeTuple(NamedTuple):
    start: int
    end: int
