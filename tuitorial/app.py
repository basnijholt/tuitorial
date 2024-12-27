"""App for presenting code tutorials."""

import shutil
from pathlib import Path
from typing import ClassVar, Literal, NamedTuple

import rich
from PIL import Image as PILImage
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.css.scalar import Scalar
from textual.widgets import Footer, Header, Markdown, Static, TabbedContent, TabPane, Tabs
from textual_image.widget import Image

from .highlighting import Focus
from .widgets import CodeDisplay


class Step(NamedTuple):
    """A single step in a tutorial, containing a description and focus patterns."""

    description: str
    focuses: list[Focus]


class ImageStep(NamedTuple):
    """A step that displays an image."""

    description: str
    image: str | Path | PILImage.Image
    width: int | str | None = None
    height: int | str | None = None
    halign: Literal["left", "center", "right"] | None = None


class MarkdownStep(NamedTuple):
    """A step that displays a markdown string."""

    description: str
    markdown: str


class Chapter(Container):
    """A chapter of a tutorial, containing multiple steps."""

    def __init__(self, title: str, code: str, steps: list[Step | ImageStep | MarkdownStep]) -> None:
        super().__init__()
        self.title = title or f"Untitled {id(self)}"
        self.code = code
        self.steps = steps
        self.current_index = 0
        self.code_display = CodeDisplay(self.code, [], dim_background=True)
        self.markdown_container = Container(Markdown(id="markdown"), id="markdown-container")
        # Create a container for the image widget instead of the Image itself
        # because of issue https://github.com/lnqs/textual-image/issues/43
        self.image_container = Container(id="image-container")
        self.image_container.visible = False  # Hide the container initially
        self.markdown_container.visible = False
        self.description = Static("", id="description")

    @property
    def current_step(self) -> Step | ImageStep | MarkdownStep:
        """Get the current step."""
        if not self.steps:
            return Step("", [])  # Return an empty Step object if no steps
        return self.steps[self.current_index]

    async def on_mount(self) -> None:
        """Mount the chapter."""
        await self.update_display()

    async def on_resize(self) -> None:
        """Called when the app is resized."""
        await self.update_display()

    def _set_description_height(self) -> None:
        """Set the height of the description."""
        padding_and_counter = 5  # 4 for padding and 1 for the step counter
        height_description = _calculate_height(self.steps, self.description.size.width)
        max_description_height = height_description + padding_and_counter
        self.description.styles.height = Scalar.from_number(max_description_height)

    async def update_display(self) -> None:
        """Update the display with current focus or image."""
        step = self.current_step
        if isinstance(step, Step):
            self.code_display.visible = True
            self.image_container.visible = False
            self.markdown_container.visible = False
            self.code_display.update_focuses(step.focuses)
        elif isinstance(step, MarkdownStep):
            self.code_display.visible = False
            self.image_container.visible = False
            self.markdown_container.visible = True
            markdown_widget = self.query_one("#markdown", Markdown)
            await markdown_widget.update(step.markdown)
        elif isinstance(step, ImageStep):
            self.code_display.visible = False
            self.markdown_container.visible = False
            self.image_container.visible = True

            # Remove the old image widget (if any) and add a new one
            await self.image_container.remove_children()
            image_widget = Image(step.image, id="image")
            if self.image_container.is_mounted:
                await self.image_container.mount(image_widget)

            # Set the image size using styles
            if step.width is not None:
                width = f"{step.width}" if isinstance(step.width, int) else step.width
                image_widget.styles.width = Scalar.parse(width)
            if step.height is not None:
                height = f"{step.height}" if isinstance(step.height, int) else step.height
                image_widget.styles.height = Scalar.parse(height)
            if step.halign is not None:
                image_widget.styles.align_horizontal = step.halign

        self.description.update(
            f"Step {self.current_index + 1}/{len(self.steps)}\n{step.description}",
        )
        self._set_description_height()

    async def next_step(self) -> None:
        """Handle next focus action."""
        self.current_index = (self.current_index + 1) % len(self.steps)
        await self.update_display()

    async def previous_step(self) -> None:
        """Handle previous focus action."""
        self.current_index = (self.current_index - 1) % len(self.steps)
        await self.update_display()

    async def reset_step(self) -> None:
        """Reset to first focus pattern."""
        self.current_index = 0
        await self.update_display()

    async def toggle_dim(self) -> None:
        """Toggle dim background."""
        if isinstance(self.current_step, Step):
            self.code_display.dim_background = not self.code_display.dim_background
            self.code_display.refresh()
            await self.update_display()

    def compose(self) -> ComposeResult:
        """Compose the chapter display."""
        yield Container(
            self.description,
            self.image_container,
            self.code_display,
            self.markdown_container,
        )


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
        self.chapters: list[Chapter] = chapters
        self.current_chapter_index: int = 0

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        with TabbedContent():
            for i, chapter in enumerate(self.chapters):
                with TabPane(chapter.title, id=f"chapter_{i}"):
                    yield chapter
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


def _calculate_height(
    steps: list[Step | ImageStep | MarkdownStep],
    width: int | None = None,
) -> int:
    """Calculate the height of the chapter."""
    if width is None or width == 0:
        width = shutil.get_terminal_size().columns - 8
    n_lines = 0
    console = rich.get_console()
    for step in steps:
        if isinstance(step, Step):
            rich_text = Text.from_markup(step.description)
            lines = rich_text.wrap(console, width=width)
            n_lines = max(n_lines, len(lines))
    return n_lines
