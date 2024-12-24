"""App for presenting code tutorials."""

from typing import ClassVar, NamedTuple

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
        self.current_step_index = 0
        self.code_display = CodeDisplay(
            self.code,
            self.current_step.focuses,
            dim_background=True,
        )
        self.update_display()

    @property
    def current_step(self) -> Step:
        """Get the current step."""
        return self.steps[self.current_step_index]

    def update_display(self) -> None:
        """Update the display with current focus."""
        self.code_display.update_focuses(self.current_step.focuses)

    def next_step(self) -> None:
        """Handle next focus action."""
        self.current_step_index = (self.current_step_index + 1) % len(self.steps)
        self.update_display()

    def previous_step(self) -> None:
        """Handle previous focus action."""
        self.current_step_index = (self.current_step_index - 1) % len(self.steps)
        self.update_display()

    def reset_step(self) -> None:
        """Reset to first focus pattern."""
        self.current_step_index = 0
        self.update_display()

    def toggle_dim(self) -> None:
        """Toggle dim background."""
        self.code_display.dim_background = not self.code_display.dim_background
        self.code_display.refresh()
        self.update_display()

    def compose(self) -> ComposeResult:
        """Compose the chapter display."""
        yield Container(
            Static(
                f"Step {self.current_step_index + 1}/{len(self.steps)}\n{self.current_step.description}",
                id="description",
            ),
            self.code_display,
        )


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
        Binding("right", "next_focus", "Next Focus"),
        Binding("left", "previous_focus", "Previous Focus"),
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
            for chapter in self.chapters:
                with TabPane(chapter.title):
                    yield from chapter.compose()
        yield Footer()

    @property
    def current_chapter(self) -> Chapter:
        """Get the current chapter."""
        return self.chapters[self.current_chapter_index]

    def on_mount(self) -> None:
        """Called when app is mounted."""
        # Initialize all chapters
        for chapter in self.chapters:
            chapter.update_display()
        self.query_one(TabbedContent).focus()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle chapter changes."""
        if event.tab is None:
            return

        # Find the chapter by matching the tab's ID
        tab_id = event.tab.id
        for index, chapter in enumerate(self.chapters):
            if chapter.title.lower().replace(" ", "-") == tab_id:
                self.current_chapter_index = index
                self.current_chapter.reset_step()
                break

    def update_display(self) -> None:
        """Update the display with current focus."""
        chapter = self.current_chapter
        # Update description
        description = self.query_one(f"#{chapter.title.lower().replace(' ', '-')}-description")
        if description:
            description.update(
                f"Step {chapter.current_step_index + 1}/{len(chapter.steps)}\n"
                f"{chapter.current_step.description}",
            )
        # Update code display
        chapter.code_display.update_focuses(chapter.current_step.focuses)
        chapter.code_display.refresh()

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
