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
        height: 100%;
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
        initial_chapter: int | None = None,
        initial_step: int = 0,
    ) -> None:
        super().__init__()
        self.chapters: list[Chapter] = chapters
        if initial_chapter is None:
            initial_chapter = 0 if title_slide is None else -1
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

    async def set_chapter(self, chapter_index: int, *, nearest: bool = False) -> None:
        """Set the current chapter and update the display."""
        if chapter_index == -1 and self.title_slide:
            self.current_chapter_index = -1
            self.query_one(TabbedContent).active = "title-slide-tab"
        elif 0 <= chapter_index < len(self.chapters):
            self.current_chapter_index = chapter_index
            self.query_one(TabbedContent).active = f"chapter_{chapter_index}"
            await self.current_chapter.update_display()
        elif nearest:
            chapter_index = max(0, min(len(self.chapters) - 1, chapter_index))
            await self.set_chapter(chapter_index)
        else:
            msg = f"Invalid chapter index: {chapter_index}"
            raise ValueError(msg)

    async def set_step(self, step_index: int) -> None:
        """Set the current step and update the display."""
        if self.current_chapter_index >= 0:
            n_steps = len(self.current_chapter.steps) - 1
            self.current_chapter.current_index = max(0, min(step_index, n_steps))
            await self.update_display()

    def on_ready(self) -> None:
        """Handle on ready event."""
        self.set_title_slide_height()

    def set_title_slide_height(self) -> None:
        """Set the height of the title slide tab to match the title slide to center in middle."""
        if self.title_slide:
            tab = self.query_one("#title-slide-tab")
            tabbed = self.query_one(TabbedContent)
            tab.styles.height = Scalar.from_number(tabbed.size.height)

    async def on_mount(self) -> None:
        """Set initial chapter and step."""
        if 0 <= self.initial_chapter < len(self.chapters):
            await self.set_chapter(self.initial_chapter)
            await self.set_step(self.initial_step)
        elif self.title_slide:
            await self.set_chapter(-1)

    @property
    def current_chapter(self) -> Chapter:
        """Get the current chapter."""
        return self.chapters[self.current_chapter_index]

    @on(TabbedContent.TabActivated)
    @on(Tabs.TabActivated)
    def on_change(self, event: TabbedContent.TabActivated | Tabs.TabActivated) -> None:
        """Handle tab change event and set the current chapter index."""
        tab_id = event.pane.id
        if tab_id == "title-slide-tab":
            self.current_chapter_index = -1
            return

        assert tab_id.startswith("chapter_")
        index = int(tab_id.split("_")[-1])
        self.current_chapter_index = int(index)

    def current_tab_pane(self) -> TabPane:
        """Get the current tab id."""
        tab_id = self.query_one(TabbedContent).active
        return self.query_one(f"#{tab_id}")

    async def update_display(self) -> None:
        """Update the display with current focus."""
        await self.current_chapter.update_display()

    async def action_next_focus(self) -> None:
        """Handle next focus action."""
        if self.current_chapter_index >= 0:
            await self.current_chapter.next_step()
            await self.update_display()

    async def action_previous_focus(self) -> None:
        """Handle previous focus action."""
        if self.current_chapter_index >= 0:
            await self.current_chapter.previous_step()
            await self.update_display()

    async def action_reset_focus(self) -> None:
        """Reset to first focus pattern."""
        if self.current_chapter_index >= 0:
            await self.current_chapter.reset_step()

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
