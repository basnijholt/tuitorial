"""App for presenting code tutorials."""

from typing import ClassVar, NamedTuple

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane, Tabs

from .highlighting import Focus
from .widgets import CodeDisplay


class Step(NamedTuple):
    """A single step in a tutorial, containing a description and focus patterns."""

    description: str
    focuses: list[Focus]


class Chapter:
    """A chapter of a tutorial, containing multiple steps."""

    def __init__(self, title: str, code: str, steps: list[Step]) -> None:
        self.title = title or f"Untitled {id(self)}"
        self.code = code
        self.steps = steps
        self.current_index = 0
        self.code_display = CodeDisplay(
            self.code,
            self.current_step.focuses,
            dim_background=True,
        )
        self.description = Static("", id="description")
        self.update_display()

    @property
    def current_step(self) -> Step:
        """Get the current step."""
        return self.steps[self.current_index]

    def update_display(self) -> None:
        """Update the display with current focus."""
        self.code_display.update_focuses(self.current_step.focuses)
        self.description.update(
            f"Step {self.current_index + 1}/{len(self.steps)}\n{self.current_step.description}",
        )

    def next_step(self) -> None:
        """Handle next focus action."""
        self.current_index = (self.current_index + 1) % len(self.steps)
        self.update_display()

    def previous_step(self) -> None:
        """Handle previous focus action."""
        self.current_index = (self.current_index - 1) % len(self.steps)
        self.update_display()

    def reset_step(self) -> None:
        """Reset to first focus pattern."""
        self.current_index = 0
        self.update_display()

    def toggle_dim(self) -> None:
        """Toggle dim background."""
        self.code_display.dim_background = not self.code_display.dim_background
        self.code_display.refresh()
        self.update_display()

    def compose(self) -> ComposeResult:
        """Compose the chapter display."""
        yield Container(self.description, self.code_display)


class TutorialApp(App):
    """A Textual app for presenting code tutorials."""

    CSS = """
    Tabs {
        dock: top;
    }

    TabPane {
        padding: 1 2;
    }

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

    TabbedContent {
        height: 1fr;
    }
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("q", "quit", "Quit"),
        Binding("down", "next_focus", "Next Focus"),
        Binding("up", "previous_focus", "Previous Focus"),
        Binding("d", "toggle_dim", "Toggle Dim"),
        ("r", "reset_focus", "Reset Focus"),
    ]

    def __init__(self, chapters: list[Chapter]) -> None:
        super().__init__()
        self.chapters = chapters
        self.current_chapter_index = 0

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        with TabbedContent():
            for i, chapter in enumerate(self.chapters):
                with TabPane(chapter.title, id=f"chapter_{i}"):
                    yield from chapter.compose()
        yield Footer()

    @property
    def current_chapter(self) -> Chapter:
        """Get the current chapter."""
        return self.chapters[self.current_chapter_index]

    @on(TabbedContent.TabActivated)
    @on(Tabs.TabActivated)
    def on_change(self, event: TabbedContent.TabActivated | Tabs.TabActivated) -> None:
        """Handle tab change event."""
        tab_id = event.pane.id
        assert tab_id.startswith("chapter_")
        index = tab_id.split("_")[-1]
        self.current_chapter_index = int(index)

    def update_display(self) -> None:
        """Update the display with current focus."""
        self.current_chapter.update_display()

    def action_next_focus(self) -> None:
        """Handle next focus action."""
        self.current_chapter.next_step()
        self.update_display()

    def action_previous_focus(self) -> None:
        """Handle previous focus action."""
        self.current_chapter.previous_step()
        self.update_display()

    def action_reset_focus(self) -> None:
        """Reset to first focus pattern."""
        self.current_chapter.reset_step()
        self.update_display()

    def action_toggle_dim(self) -> None:
        """Toggle dim background."""
        self.current_chapter.toggle_dim()
        self.update_display()
