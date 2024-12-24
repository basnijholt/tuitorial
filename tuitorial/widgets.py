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

        # First collect all ranges that need highlighting with their styles
        highlighted_ranges = set()

        # Process all focus types and collect their ranges
        for focus in self.focuses:
            if focus.type == FocusType.LITERAL:
                pattern = re.escape(str(focus.pattern))
                if getattr(focus, "word_boundary", False):
                    pattern = rf"\b{pattern}\b"
                for match in re.finditer(pattern, self.code):
                    highlighted_ranges.add((match.start(), match.end(), focus.style))
            elif focus.type == FocusType.REGEX:
                pattern = (
                    focus.pattern  # type: ignore[assignment]
                    if isinstance(focus.pattern, Pattern)
                    else re.compile(focus.pattern)  # type: ignore[type-var]
                )
                assert isinstance(pattern, Pattern)
                for match in pattern.finditer(self.code):
                    highlighted_ranges.add((match.start(), match.end(), focus.style))
            elif focus.type == FocusType.LINE:
                assert isinstance(focus.pattern, int)
                line_number = int(focus.pattern)
                lines = self.code.split("\n")
                if 0 <= line_number < len(lines):
                    start = sum(len(line) + 1 for line in lines[:line_number])
                    end = start + len(lines[line_number])
                    highlighted_ranges.add((start, end, focus.style))
            elif focus.type == FocusType.RANGE:
                assert isinstance(focus.pattern, tuple)
                start, end = focus.pattern
                highlighted_ranges.add((start, end, focus.style))

        # Sort ranges by start position and length (longer matches first)
        sorted_ranges = sorted(
            highlighted_ranges,
            key=lambda x: (x[0], -(x[1] - x[0])),  # Sort by position and prefer longer matches
        )

        # Apply highlights without overlaps
        current_pos = 0
        processed_ranges = set()

        for start, end, style in sorted_ranges:
            # Skip if this range overlaps with an already processed range
            if any(
                (p_start <= start < p_end) or (p_start < end <= p_end)
                for p_start, p_end in processed_ranges
            ):
                continue

            # Add dim style to gap before this highlight if needed
            if self.dim_background and current_pos < start:
                text.stylize(Style(dim=True), current_pos, start)

            # Add the highlight style
            text.stylize(style, start, end)
            processed_ranges.add((start, end))
            current_pos = max(current_pos, end)

        # Dim any remaining text
        if self.dim_background and current_pos < len(self.code):
            text.stylize(Style(dim=True), current_pos, len(self.code))

        return text

    def render(self) -> Text:
        """Render the widget content."""
        return self.highlight_code()
