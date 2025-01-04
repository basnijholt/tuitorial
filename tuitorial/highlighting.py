"""Highlighting utilities for the tutorial."""

from __future__ import annotations

import re
from re import Pattern
from typing import ClassVar

from pydantic import BaseModel, Field
from rich.style import Style


class BaseFocus(BaseModel):
    """Base class for all focus types."""

    style: Style = Field(default=Style(color="yellow", bold=True))


class LiteralFocus(BaseFocus):
    """Focus for literal string matches."""

    pattern: str
    match_index: int | list[int] | None = None
    word_boundary: bool = False


class RegexFocus(BaseFocus):
    """Focus for regex pattern matches."""

    pattern: Pattern
    match_index: int | list[int] | None = None


class LineFocus(BaseFocus):
    """Focus for specific line numbers."""

    line_number: int


class RangeFocus(BaseFocus):
    """Focus for character ranges."""

    start: int
    end: int


class StartsWithFocus(BaseFocus):
    """Focus for text that starts with a pattern."""

    text: str
    from_start_of_line: bool = False


class BetweenFocus(BaseFocus):
    """Focus for text between patterns."""

    start_pattern: str
    end_pattern: str
    inclusive: bool = True
    multiline: bool = True
    match_index: int | None = None
    greedy: bool = False


class LineContainingFocus(BaseFocus):
    """Focus for lines containing a pattern."""

    pattern: str
    lines_before: int = 0
    lines_after: int = 0
    match_index: int | None = None


class LineContainingRegexFocus(BaseFocus):
    """Focus for lines containing a regex pattern."""

    pattern: str
    lines_before: int = 0
    lines_after: int = 0
    match_index: int | None = None


class SyntaxFocus(BaseFocus):
    """Focus for syntax highlighting."""

    lexer: str = "python"
    theme: str | None = None
    line_numbers: bool = False
    start_line: int | None = None
    end_line: int | None = None


class MarkdownFocus(BaseFocus):
    """Focus for Markdown blocks."""


Focus = (
    LiteralFocus
    | RegexFocus
    | LineFocus
    | RangeFocus
    | StartsWithFocus
    | BetweenFocus
    | LineContainingFocus
    | LineContainingRegexFocus
    | SyntaxFocus
    | MarkdownFocus
)


def validate_focuses(focuses: list[Focus]) -> None:
    """Validate that there's at most one markdown or syntax focus."""
    markdown_focuses = sum(1 for f in focuses if isinstance(f, MarkdownFocus))
    syntax_focuses = sum(1 for f in focuses if isinstance(f, SyntaxFocus))

    if markdown_focuses > 1:
        msg = "Only one markdown focus is allowed per step."
        raise ValueError(msg)
    if syntax_focuses > 1:
        msg = "Only one syntax focus is allowed per step."
        raise ValueError(msg)


class Focus:
    """A pattern to focus on with its style."""

    _DEFAULT_STYLE: ClassVar[Style] = Style(color="yellow", bold=True)

    @classmethod
    def literal(
        cls,
        text: str,
        style: Style = Style(color="yellow", bold=True),  # noqa: B008
        *,
        word_boundary: bool = False,
        match_index: int | list[int] | None = None,
    ) -> LiteralFocus | RegexFocus:
        """Create a focus for a literal string.

        Parameters
        ----------
        text
            The text to match
        style
            The style to apply to the matched text
        word_boundary
            If True, only match the text when it appears as a word
        match_index
            If provided, only highlight the nth match (0-based) or matches specified by the list.
            If None, highlight all matches.

        """
        if word_boundary:
            pattern = re.compile(rf"\b{re.escape(text)}\b")
            return RegexFocus(pattern=pattern, style=style, match_index=match_index)
        return LiteralFocus(
            pattern=text,
            style=style,
            match_index=match_index,
            word_boundary=word_boundary,
        )

    @classmethod
    def regex(
        cls,
        pattern: str | Pattern,
        style: Style = Style(color="green", bold=True),  # noqa: B008
    ) -> RegexFocus:
        """Create a focus for a regular expression.

        Parameters
        ----------
        pattern
            The regular expression pattern to match
        style
            The style to apply to the matched text

        """
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return RegexFocus(pattern=pattern, style=style)

    @classmethod
    def line(
        cls,
        line_number: int,
        style: Style = Style(color="cyan", bold=True),  # noqa: B008
    ) -> LineFocus:
        """Create a focus for a line number.

        Parameters
        ----------
        line_number
            The line number to highlight (0-based)
        style
            The style to apply to the line

        """
        return LineFocus(line_number=line_number, style=style)

    @classmethod
    def range(
        cls,
        start: int,
        end: int,
        style: Style = Style(color="magenta", bold=True),  # noqa: B008
    ) -> RangeFocus:
        """Create a focus for a range of characters.

        Parameters
        ----------
        start
            The starting character position
        end
            The ending character position
        style
            The style to apply to the range

        """
        return RangeFocus(start=start, end=end, style=style)

    @classmethod
    def startswith(
        cls,
        text: str,
        style: Style = Style(color="blue", bold=True),  # noqa: B008
        *,
        from_start_of_line: bool = False,
    ) -> StartsWithFocus:
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
        return StartsWithFocus(text=text, style=style, from_start_of_line=from_start_of_line)

    @classmethod
    def between(
        cls,
        start_pattern: str,
        end_pattern: str,
        style: Style = Style(color="blue", bold=True),  # noqa: B008
        *,
        inclusive: bool = True,
        multiline: bool = True,
        match_index: int | None = None,
        greedy: bool = False,
    ) -> BetweenFocus:
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
        return BetweenFocus(
            start_pattern=start_pattern,
            end_pattern=end_pattern,
            style=style,
            inclusive=inclusive,
            multiline=multiline,
            match_index=match_index,
            greedy=greedy,
        )

    @classmethod
    def line_containing(
        cls,
        pattern: str,
        style: Style = Style(color="yellow", bold=True),  # noqa: B008
        *,
        lines_before: int = 0,
        lines_after: int = 0,
        regex: bool = False,
        match_index: int | None = None,
    ) -> LineContainingFocus | LineContainingRegexFocus:
        """Select the entire line containing a pattern and optionally surrounding lines.

        Parameters
        ----------
        pattern
            The text pattern to search for
        style
            The style to apply to the matched lines
        lines_before
            Number of lines to include before the matched line
        lines_after
            Number of lines to include after the matched line
        regex
            If True, treat pattern as a regular expression
        match_index
            If provided, only highlight the nth match (0-based).
            If None, highlight all matches.

        """
        if regex:
            return LineContainingRegexFocus(
                pattern=pattern,
                style=style,
                lines_before=lines_before,
                lines_after=lines_after,
                match_index=match_index,
            )
        return LineContainingFocus(
            pattern=pattern,
            style=style,
            lines_before=lines_before,
            lines_after=lines_after,
            match_index=match_index,
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
    ) -> SyntaxFocus:
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
        return SyntaxFocus(
            lexer=lexer,
            theme=theme,
            line_numbers=line_numbers,
            start_line=start_line,
            end_line=end_line,
        )

    @classmethod
    def markdown(cls) -> MarkdownFocus:
        """Create a focus for a Markdown block."""
        return MarkdownFocus()
