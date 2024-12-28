"""App for presenting code tutorials."""

from typing import ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.css.scalar import Scalar
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

    def __init__(self, chapters: list[Chapter], title_slide: TitleSlide | None = None) -> None:
        super().__init__()
        self.chapters: list[Chapter] = chapters
        self.current_chapter_index: int = 0
        self.title_slide = title_slide

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

    def on_ready(self) -> None:
        """Handle on ready event."""
        if self.title_slide:
            # Set the height of the tab to match the height of the title slide
            # to make the title slide appear in the middle of the screen.
            tab = self.query_one("#title-slide-tab")
            tabbed = self.query_one(TabbedContent)
            tab.styles.height = Scalar.from_number(tabbed.size.height)

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
