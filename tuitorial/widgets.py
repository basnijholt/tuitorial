"""Custom widgets for the Tuitorial application."""

import re
from re import Pattern

from rich.style import Style
from rich.text import Text
from textual.widgets import Static

from .highlighting import Focus, FocusType


class CodeDisplay(Static):
    """A widget to display code with highlighting."""

    def __init__(self, code: str, focuses: list[Focus] | None = None) -> None:
        super().__init__()
        self.code = code
        self.focuses = focuses or []

    def update_focuses(self, focuses: list[Focus]) -> None:
        """Update the focuses and refresh the display."""
        self.focuses = focuses
        self.refresh()  # Tell Textual to refresh this widget

    def highlight_code(self) -> Text:
        """Apply highlighting to the code."""
        text = Text(self.code)
        text.stylize(Style(dim=True))

        for focus in self.focuses:
            if focus.type == FocusType.LITERAL:
                pattern = re.escape(str(focus.pattern))
                for match in re.finditer(pattern, self.code):
                    text.stylize(focus.style, match.start(), match.end())

            elif focus.type == FocusType.REGEX:
                pattern = (
                    focus.pattern
                    if isinstance(focus.pattern, Pattern)
                    else re.compile(focus.pattern)
                )
                for match in pattern.finditer(self.code):
                    text.stylize(focus.style, match.start(), match.end())

            elif focus.type == FocusType.LINE:
                line_number = int(focus.pattern)
                lines = self.code.split("\n")
                if 0 <= line_number < len(lines):
                    start = sum(len(line) + 1 for line in lines[:line_number])
                    end = start + len(lines[line_number])
                    text.stylize(focus.style, start, end)

            elif focus.type == FocusType.RANGE:
                start, end = focus.pattern
                text.stylize(focus.style, start, end)

        return text

    def render(self) -> Text:
        """Render the widget content."""
        return self.highlight_code()
