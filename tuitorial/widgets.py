"""Custom widgets for the Tuitorial application."""

import re
from re import Pattern

from rich.style import Style
from rich.text import Text
from textual.widgets import Static

from .highlighting import Focus, FocusType


class CodeDisplay(Static):
    """A widget to display code with highlighting.

    Parameters
    ----------
    code
        The code to display
    focuses
        List of Focus objects to apply
    dim_background
        Whether to dim the non-highlighted text

    """

    def __init__(
        self,
        code: str,
        focuses: list[Focus] | None = None,
        *,
        dim_background: bool = True,
    ) -> None:
        super().__init__()
        self.code = code
        self.focuses = focuses or []
        self.dim_background = dim_background

    def update_focuses(self, focuses: list[Focus]) -> None:
        """Update the focuses and refresh the display."""
        self.focuses = focuses
        self.refresh()  # Tell Textual to refresh this widget

    def highlight_code(self) -> Text:
        """Apply highlighting to the code."""
        text = Text(self.code)

        # Collect and sort ranges
        ranges = _collect_highlight_ranges(self.code, self.focuses)
        sorted_ranges = _sort_ranges(ranges)

        # Apply highlights
        _apply_highlights(text, self.code, sorted_ranges, self.dim_background)

        return text

    def render(self) -> Text:
        """Render the widget content."""
        return self.highlight_code()


def _collect_literal_ranges(code: str, focus: Focus) -> set[tuple[int, int, Style]]:
    """Collect ranges for literal focus type."""
    ranges = set()
    pattern = re.escape(str(focus.pattern))
    if getattr(focus, "word_boundary", False):
        pattern = rf"\b{pattern}\b"
    for match in re.finditer(pattern, code):
        ranges.add((match.start(), match.end(), focus.style))
    return ranges


def _collect_regex_ranges(code: str, focus: Focus) -> set[tuple[int, int, Style]]:
    """Collect ranges for regex focus type."""
    ranges = set()
    pattern = (
        focus.pattern  # type: ignore[assignment]
        if isinstance(focus.pattern, Pattern)
        else re.compile(focus.pattern)  # type: ignore[type-var]
    )
    assert isinstance(pattern, Pattern)
    for match in pattern.finditer(code):
        ranges.add((match.start(), match.end(), focus.style))
    return ranges


def _collect_line_ranges(code: str, focus: Focus) -> set[tuple[int, int, Style]]:
    """Collect ranges for line focus type."""
    ranges = set()
    assert isinstance(focus.pattern, int)
    line_number = int(focus.pattern)
    lines = code.split("\n")
    if 0 <= line_number < len(lines):
        start = sum(len(line) + 1 for line in lines[:line_number])
        end = start + len(lines[line_number])
        ranges.add((start, end, focus.style))
    return ranges


def _collect_range_ranges(_: str, focus: Focus) -> set[tuple[int, int, Style]]:
    """Collect ranges for range focus type."""
    assert isinstance(focus.pattern, tuple)
    start, end = focus.pattern
    return {(start, end, focus.style)}


def _collect_highlight_ranges(
    code: str,
    focuses: list[Focus],
) -> set[tuple[int, int, Style]]:
    """Collect all ranges that need highlighting with their styles."""
    ranges = set()
    focus_type_handlers = {
        FocusType.LITERAL: _collect_literal_ranges,
        FocusType.REGEX: _collect_regex_ranges,
        FocusType.LINE: _collect_line_ranges,
        FocusType.RANGE: _collect_range_ranges,
    }

    for focus in focuses:
        handler = focus_type_handlers[focus.type]
        ranges.update(handler(code, focus))

    return ranges


def _sort_ranges(
    ranges: set[tuple[int, int, Style]],
) -> list[tuple[int, int, Style]]:
    """Sort ranges by position and length (longer matches first)."""
    return sorted(ranges, key=lambda x: (x[0], -(x[1] - x[0])))


def _is_overlapping(
    start: int,
    end: int,
    processed_ranges: set[tuple[int, int]],
) -> bool:
    """Check if a range overlaps with any processed ranges in an invalid way.

    Allows partial overlaps but prevents:
    1. Complete containment of the new range
    2. Complete containment of an existing range
    """
    for p_start, p_end in processed_ranges:
        # Skip if either range completely contains the other
        if (p_start <= start and p_end >= end) or (start <= p_start and end >= p_end):
            return True

        # Allow partial overlaps
        continue

    return False


def _apply_highlights(
    text: Text,
    code: str,
    sorted_ranges: list[tuple[int, int, Style]],
    dim_background: bool,  # noqa: FBT001
) -> None:
    """Apply highlights without overlaps and dim the background."""
    current_pos = 0
    processed_ranges: set[tuple[int, int]] = set()

    for start, end, style in sorted_ranges:
        # Skip if this range overlaps with an already processed range
        if _is_overlapping(start, end, processed_ranges):
            continue

        # Add dim style to gap before this highlight if needed
        if dim_background and current_pos < start:
            text.stylize(Style(dim=True), current_pos, start)

        # Add the highlight style
        text.stylize(style, start, end)
        processed_ranges.add((start, end))
        current_pos = max(current_pos, end)

    # Dim any remaining text
    if dim_background and current_pos < len(code):
        text.stylize(Style(dim=True), current_pos, len(code))
