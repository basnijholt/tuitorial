"""App for presenting code tutorials."""

from typing import ClassVar, NamedTuple

from PIL import Image as PILImage
from rich.console import Group
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane, Tabs
from textual_image.renderable import Image as RichImage

from .highlighting import Focus
from .widgets import CodeDisplay


class Step(NamedTuple):
    """A single step in a tutorial, containing a description and focus patterns."""

    description: str
    focuses: list[Focus]


class ImageStep(NamedTuple):
    """A step in a tutorial that displays an image."""

    description: str
    image: RichImage  # Use the Rich renderable from textual-image

    @classmethod
    def from_file(cls, description: str, image_path: str, **kwargs):
        """Creates an ImageStep from an image file.

        Args:
            description: The step description.
            image_path: Path to the image file.
            **kwargs: Keyword arguments passed to textual_image.renderable.Image

        """
        pil_image = PILImage.open(image_path)
        return cls(description, RichImage(pil_image, **kwargs))


class Chapter:
    """A chapter of a tutorial, containing multiple steps."""

    def __init__(
        self,
        title: str,
        code: str,
        steps: list[Step],
        image_steps: list[ImageStep] | None = None,
    ) -> None:
        self.title = title or f"Untitled {id(self)}"
        self.code = code
        self.steps = steps
        self.current_index = 0
        self.image_steps = image_steps or []
        self.current_image_index = 0
        self.tutorial_display = TutorialDisplay(
            self,
            dim_background=True,
        )
        self.description = Static("", id="description")
        self.update_display()

    @property
    def current_step(self) -> Step:
        """Get the current step."""
        if not self.steps:
            return Step("", [])  # Return an empty Step object
        return self.steps[self.current_index]

    @property
    def current_image_step(self) -> ImageStep | None:
        """Get the current image step."""
        if not self.image_steps:
            return None
        if self.current_image_index < 0 or self.current_image_index >= len(self.image_steps):
            return None  # or handle the out-of-bounds case as you prefer
        return self.image_steps[self.current_image_index]

    def update_display(self) -> None:
        """Update the display with current focus and image (if any)."""
        description_lines = []

        if self.current_step:
            self.tutorial_display.update_focuses(self.current_step.focuses)
            description_lines.append(
                f"Step {self.current_index + 1}/{len(self.steps)}: {self.current_step.description}",
            )

        if self.current_image_step:
            description_lines.append(
                f"Image Step {self.current_image_index + 1}/{len(self.image_steps)}: {self.current_image_step.description}",
            )

        self.description.update("\n".join(description_lines))
        self.tutorial_display.refresh()

    def next_step(self) -> None:
        """Handle next focus action."""
        if self.current_step and self.current_index < len(self.steps) - 1:
            self.current_index += 1
            self.update_display()
        elif self.current_image_step and self.current_image_index < len(self.image_steps) - 1:
            self.current_image_index += 1
            self.update_display()
        else:
            if self.current_step:
                self.current_index = 0
            elif self.current_image_step:
                self.current_image_index = 0
            self.update_display()

    def previous_step(self) -> None:
        """Handle previous focus action."""
        if self.current_step and self.current_index > 0:
            self.current_index -= 1
            self.update_display()
        elif self.current_image_step and self.current_image_index > 0:
            self.current_image_index -= 1
            self.update_display()
        else:
            if self.current_step:
                self.current_index = len(self.steps) - 1
            elif self.current_image_step:
                self.current_image_index = len(self.image_steps) - 1
            self.update_display()

    def reset_step(self) -> None:
        """Reset to first focus pattern."""
        self.current_index = 0
        self.update_display()

    def toggle_dim(self) -> None:
        """Toggle dim background."""
        self.tutorial_display.dim_background = not self.tutorial_display.dim_background
        self.tutorial_display.refresh()
        self.update_display()

    def compose(self) -> ComposeResult:
        """Compose the chapter display."""
        yield Container(self.description, self.tutorial_display)


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
                    yield chapter.tutorial_display
                    yield chapter.description
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


class TutorialDisplay(Static):
    """Widget to display code with highlighting or images."""

    def __init__(
        self,
        chapter: Chapter,
        *,
        dim_background: bool = True,
    ) -> None:
        super().__init__()
        self.chapter = chapter
        self.dim_background = dim_background

    def render(self) -> Group:
        """Render the current step, either code or image."""
        renderables = []
        current_step = self.chapter.current_step
        current_image_step = self.chapter.current_image_step

        if current_step:
            tutorial_display = CodeDisplay(
                self.chapter.code,
                current_step.focuses,
                dim_background=self.dim_background,
            )
            renderables.append(tutorial_display.highlight_code())

        if current_image_step:
            renderables.append(current_image_step.image)

        return Group(*renderables)
