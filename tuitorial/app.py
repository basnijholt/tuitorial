"""App for presenting code tutorials."""

import time
from typing import ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.css.scalar import Scalar
from textual.events import MouseScrollDown, MouseScrollUp
from textual.widgets import Footer, Header, TabbedContent, TabPane, Tabs

from .widgets import Chapter, TitleSlide


class TuitorialApp(App):
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

    ContentContainer {
        height: auto;
    }

    #image-container {
        align: center middle;
    }

    #image {
        width: auto;
        height: auto;
    }

    #markdown-container {
        height: 1fr;
    }

    #title-rich-log {
        overflow-y: auto;
        background: black 0%;
    }

    #title-slide-tab {
        align: center middle;
    }
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("q", "quit", "Quit"),
        Binding("down", "next_focus", "Next Focus"),
        Binding("up", "previous_focus", "Previous Focus"),
        Binding("d", "toggle_dim", "Toggle Dim"),
        ("r", "reset_focus", "Reset Focus"),
    ]

    def __init__(
        self,
        chapters: list[Chapter],
        title_slide: TitleSlide | None = None,
        initial_chapter: int = 0,
        initial_step: int = 0,
    ) -> None:
        super().__init__()
        self.chapters: list[Chapter] = chapters
        self.current_chapter_index: int = initial_chapter
        self.initial_chapter: int = initial_chapter
        self.initial_step: int = initial_step
        self.title_slide = title_slide
        self.is_scrolling: bool = False  # Flag to track if a scroll action is in progress
        self.last_scroll_time: float = 0.0  # Initialize the time of the last scroll event
        self.scroll_debounce_time: float = 0.1  # Minimum time between scroll events in seconds

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        with TabbedContent():
            if self.title_slide:
                with TabPane("Title Slide", id="title-slide-tab"):
                    yield self.title_slide
            for i, chapter in enumerate(self.chapters):
                with TabPane(chapter.title, id=f"chapter_{i}"):
                    yield chapter
        yield Footer()

    async def on_ready(self) -> None:
        """Handle on ready event."""
        if self.title_slide:
            # Set the height of the tab to match the height of the title slide
            # to make the title slide appear in the middle of the screen.
            tab = self.query_one("#title-slide-tab")
            tabbed = self.query_one(TabbedContent)
            tab.styles.height = Scalar.from_number(tabbed.size.height)

        # Set initial chapter and step
        if 0 <= self.initial_chapter < len(self.chapters):
            self.switch_chapter(self.initial_chapter)
            self.current_chapter.current_index = self.initial_step
            await self.current_chapter.update_display()
        elif self.title_slide:
            self.switch_chapter(-1)  # Switch to the title slide

    def switch_chapter(self, chapter_index: int) -> None:
        """Switches to the specified chapter."""
        if chapter_index == -1 and self.title_slide:
            self.query_one(TabbedContent).active = "title-slide-tab"
        elif 0 <= chapter_index < len(self.chapters):
            self.query_one(TabbedContent).active = f"chapter_{chapter_index}"

    @property
    def current_chapter(self) -> Chapter:
        """Get the current chapter."""
        return self.chapters[self.current_chapter_index]

    @on(TabbedContent.TabActivated)
    @on(Tabs.TabActivated)
    def on_change(self, event: TabbedContent.TabActivated | Tabs.TabActivated) -> None:
        """Handle tab change event."""
        tab_id = event.pane.id
        if tab_id == "title-slide-tab":
            self.current_chapter_index = -1
            return
        assert tab_id.startswith("chapter_")
        index = tab_id.split("_")[-1]
        self.current_chapter_index = int(index)

    async def update_display(self) -> None:
        """Update the display with current focus."""
        await self.current_chapter.update_display()

    async def action_next_focus(self) -> None:
        """Handle next focus action."""
        await self.current_chapter.next_step()
        await self.update_display()

    async def action_previous_focus(self) -> None:
        """Handle previous focus action."""
        await self.current_chapter.previous_step()
        await self.update_display()

    async def action_reset_focus(self) -> None:
        """Reset to first focus pattern."""
        await self.current_chapter.reset_step()
        await self.update_display()

    async def action_toggle_dim(self) -> None:
        """Toggle dim background."""
        await self.current_chapter.toggle_dim()
        await self.update_display()

    @on(MouseScrollDown)
    async def next_focus_scroll(self) -> None:
        """Handle next focus scroll event."""
        current_time = time.monotonic()
        if current_time - self.last_scroll_time >= self.scroll_debounce_time:
            # We debounce the scroll event to prevent multiple scroll events.
            # A single physical scroll event can trigger multiple scroll events (e.g., 4 for me)
            self.last_scroll_time = current_time
            await self.action_next_focus()

    @on(MouseScrollUp)
    async def previous_focus_scroll(self) -> None:
        """Handle previous focus scroll event."""
        current_time = time.monotonic()
        if current_time - self.last_scroll_time >= self.scroll_debounce_time:
            self.last_scroll_time = current_time
            await self.action_previous_focus()
