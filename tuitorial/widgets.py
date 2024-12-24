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

        # Keep track of highlighted ranges
        highlighted_ranges = set()

        # First, collect all ranges that should be highlighted
        for focus in self.focuses:
            if focus.type == FocusType.LITERAL:
                pattern = re.escape(str(focus.pattern))
                for match in re.finditer(pattern, self.code):
                    highlighted_ranges.add((match.start(), match.end()))
                    text.stylize(focus.style, match.start(), match.end())
            elif focus.type == FocusType.REGEX:
                pattern = (
                    focus.pattern  # type: ignore[assignment]
                    if isinstance(focus.pattern, Pattern)
                    else re.compile(focus.pattern)  # type: ignore[type-var]
                )
                assert isinstance(pattern, Pattern)
                for match in pattern.finditer(self.code):
                    highlighted_ranges.add((match.start(), match.end()))
                    text.stylize(focus.style, match.start(), match.end())
            elif focus.type == FocusType.LINE:
                assert isinstance(focus.pattern, int)
                line_number = int(focus.pattern)
                lines = self.code.split("\n")
                if 0 <= line_number < len(lines):
                    start = sum(len(line) + 1 for line in lines[:line_number])
                    end = start + len(lines[line_number])
                    highlighted_ranges.add((start, end))
                    text.stylize(focus.style, start, end)
            elif focus.type == FocusType.RANGE:
                assert isinstance(focus.pattern, tuple)
                start, end = focus.pattern
                highlighted_ranges.add((start, end))
                text.stylize(focus.style, start, end)

        # Then dim all non-highlighted ranges if dim_background is True
        if self.dim_background:
            current_pos = 0
            for start, end in sorted(highlighted_ranges):
                if current_pos < start:
                    text.stylize(Style(dim=True), current_pos, start)
                current_pos = end

            # Dim any remaining text after the last highlight
            if current_pos < len(self.code):
                text.stylize(Style(dim=True), current_pos, len(self.code))

        return text

    def render(self) -> Text:
        """Render the widget content."""
        return self.highlight_code()
