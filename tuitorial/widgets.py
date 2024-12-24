"""Custom widgets for the Tuitorial application."""

import re
from re import Pattern

from rich.style import Style
from rich.text import Text
from textual.widgets import Static

from .highlighting import Focus, FocusType, _BetweenTuple, _RangeTuple, _StartsWithTuple


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
    assert isinstance(focus.pattern, _RangeTuple)
    start, end = focus.pattern
    assert isinstance(start, int)
    return {(start, end, focus.style)}


def _collect_highlight_ranges(
    code: str,
    focuses: list[Focus],
) -> set[tuple[int, int, Style]]:
    """Collect all ranges that need highlighting with their styles."""
    ranges = set()
    for focus in focuses:
        match focus.type:
            case FocusType.LITERAL:
                ranges.update(_collect_literal_ranges(code, focus))
            case FocusType.REGEX:
                ranges.update(_collect_regex_ranges(code, focus))
            case FocusType.LINE:
                ranges.update(_collect_line_ranges(code, focus))
            case FocusType.RANGE:
                ranges.update(_collect_range_ranges(code, focus))
            case FocusType.STARTSWITH:
                ranges.update(_collect_startswith_ranges(code, focus))
            case FocusType.BETWEEN:
                ranges.update(_collect_between_ranges(code, focus))

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


def _collect_startswith_ranges(code: str, focus: Focus) -> set[tuple[int, int, Style]]:
    """Collect ranges for startswith focus type.

    Matches and highlights entire lines that start with the pattern
    (ignoring leading whitespace) or from the pattern to the end of line.

    Parameters
    ----------
    code
        The code to search
    focus
        Focus object containing the pattern to match and whether to match from line starts

    If from_start_of_line is True, matches the pattern at the start of any line
    (ignoring leading whitespace) and highlights the entire line.
    If from_start_of_line is False, finds all occurrences of the pattern anywhere
    and highlights from each occurrence to the end of its line.

    """
    ranges = set()
    assert isinstance(focus.pattern, _StartsWithTuple)
    text, from_start_of_line = focus.pattern
    assert isinstance(text, str)
    assert isinstance(from_start_of_line, bool)

    if from_start_of_line:
        # Process each line, keeping track of position
        pos = 0
        for line in code.splitlines(keepends=True):
            stripped = line.lstrip()
            if stripped.startswith(text):
                # Find start of the actual text in the original line
                start = pos + line.find(text)
                end = pos + len(line.rstrip("\n"))
                ranges.add((start, end, focus.style))
            pos += len(line)
    else:
        # Find all occurrences
        pos = 0
        while True:
            # Find next occurrence of pattern
            start = code.find(text, pos)
            if start == -1:
                break
            # Find the end of the line containing this occurrence
            end = code.find("\n", start)
            if end == -1:
                end = len(code)
            ranges.add((start, end, focus.style))
            pos = start + 1

    return ranges


def _collect_between_ranges(code: str, focus: Focus) -> set[tuple[int, int, Style]]:
    """Collect ranges for between focus type."""
    ranges = set()
    assert isinstance(focus.pattern, _BetweenTuple)
    start_pattern, end_pattern, inclusive, multiline, match_index, greedy = focus.pattern

    # Escape special characters if they're not already regex patterns
    if not any(c in start_pattern for c in ".^$*+?{}[]\\|()"):
        start_pattern = re.escape(start_pattern)
    if not any(c in end_pattern for c in ".^$*+?{}[]\\|()"):
        end_pattern = re.escape(end_pattern)

    # Create the regex pattern
    flags = re.MULTILINE | re.DOTALL if multiline else 0

    if inclusive:
        # Include the patterns in the match
        quantifier = ".*" if greedy else ".*?"
        pattern = f"({start_pattern})({quantifier})({end_pattern})"
    else:
        # Use positive lookbehind/ahead to match between patterns
        quantifier = ".*" if greedy else ".*?"
        pattern = f"(?<={start_pattern})({quantifier})(?={end_pattern})"

    matches = list(re.finditer(pattern, code, flags=flags))

    if match_index is not None:
        # Only include the specified match
        if 0 <= match_index < len(matches):
            match = matches[match_index]
            if inclusive:
                ranges.add((match.start(), match.end(), focus.style))
            else:
                ranges.add((match.start(1), match.end(1), focus.style))
    else:
        # Include all matches
        for match in matches:
            if inclusive:
                ranges.add((match.start(), match.end(), focus.style))
            else:
                ranges.add((match.start(1), match.end(1), focus.style))

    return ranges
