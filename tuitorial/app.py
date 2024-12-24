"""App for presenting code tutorials."""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static

from .highlighting import Focus
from .widgets import CodeDisplay


class TutorialApp(App):
    """A Textual app for presenting code tutorials."""

    CSS = """
    CodeDisplay {
        height: auto;
        margin: 1;
        background: $surface;
        color: $text;
        border: solid $primary;
        padding: 1;
    }

    #description {
        height: auto;
        margin: 1;
        background: $surface-darken-1;
        color: $text;
        border: solid $primary;
        padding: 1;
    }
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("q", "quit", "Quit"),
        Binding("right", "next_focus", "Next Focus"),
        Binding("left", "previous_focus", "Previous Focus"),
        Binding("d", "toggle_dim", "Toggle Dim"),
        ("r", "reset_focus", "Reset Focus"),
    ]

    def __init__(
        self,
        code: str,
        tutorial_steps: list[tuple[str, list[Focus]]],
        *,
        dim_background: bool = True,
    ) -> None:
        super().__init__()
        self.code = code
        self.tutorial_steps = tutorial_steps
        self.current_index = 0
        self.code_display = CodeDisplay(
            self.code,
            self.current_focuses,
            dim_background=dim_background,
        )

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield Container(
            Static(
                f"Step {self.current_index + 1}/{len(self.tutorial_steps)}\n{self.current_description}",
                id="description",
            ),
            self.code_display,
        )
        yield Footer()

    @property
    def current_focuses(self) -> list[Focus]:
        """Get the current focus patterns."""
        return self.tutorial_steps[self.current_index][1]

    @property
    def current_description(self) -> str:
        """Get the current step description."""
        return self.tutorial_steps[self.current_index][0]

    def update_display(self) -> None:
        """Update the display with current focus."""
        # Update description
        description = self.query_one("#description")
        description.update(
            f"Step {self.current_index + 1}/{len(self.tutorial_steps)}\n{self.current_description}",
        )

        # Update code highlighting
        self.code_display.update_focuses(self.current_focuses)

    def action_next_focus(self) -> None:
        """Handle next focus action."""
        self.current_index = (self.current_index + 1) % len(self.tutorial_steps)
        self.update_display()

    def action_previous_focus(self) -> None:
        """Handle previous focus action."""
        self.current_index = (self.current_index - 1) % len(self.tutorial_steps)
        self.update_display()

    def action_reset_focus(self) -> None:
        """Reset to first focus pattern."""
        self.current_index = 0
        self.update_display()

    def action_toggle_dim(self) -> None:
        """Toggle dim background."""
        self.code_display.dim_background = not self.code_display.dim_background
        self.code_display.refresh()
        self.update_display()
