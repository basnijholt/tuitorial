"""Tests for Markdown functionality in tuitorial."""

import pytest
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Markdown

from tuitorial.app import Chapter, MarkdownStep, Step, TuitorialApp
from tuitorial.highlighting import Focus


class SimpleMarkdownApp(App):
    """A simple Textual app for testing Markdown rendering."""

    def __init__(self, markdown_content: str):
        super().__init__()
        self.markdown_content = markdown_content

    def compose(self) -> ComposeResult:
        """Compose the app with a Markdown widget."""
        yield Container(Markdown(self.markdown_content))


@pytest.fixture
async def markdown_app():
    """Fixture for a simple Markdown app."""
    app = SimpleMarkdownApp("# Test Header\nSome **bold** text.")
    async with app.run_test() as pilot:
        yield pilot


async def test_markdown_rendering(markdown_app):
    """Test that Markdown content is rendered correctly."""
    markdown_widget = markdown_app.app.query_one(Markdown)
    # Check if the Markdown widget has content
    assert markdown_widget.document.root.get_children() is not None

    # You can add more specific checks based on the expected rendered output
    # For example, checking for the presence of certain elements or text


@pytest.fixture
def example_code():
    return "def test():\n    pass\n"


@pytest.fixture
def markdown_steps():
    return [
        MarkdownStep("Markdown Step 1", "# Header 1\nSome content"),
        Step("Code Step 1", [Focus.literal("def")]),
        MarkdownStep("Markdown Step 2", "## Header 2\nMore content"),
    ]


@pytest.fixture
def markdown_chapter(example_code, markdown_steps):
    return Chapter("Markdown Chapter", example_code, markdown_steps)


@pytest.mark.asyncio
async def test_markdown_chapter_init(markdown_chapter):
    """Test initialization of a chapter with MarkdownSteps."""
    app = TuitorialApp([markdown_chapter])
    async with app.run_test():
        assert len(app.chapters) == 1
        assert app.chapters[0] == markdown_chapter
        assert app.current_chapter_index == 0


@pytest.mark.asyncio
async def test_markdown_step_display(markdown_chapter):
    """Test displaying a MarkdownStep."""
    app = TuitorialApp([markdown_chapter])
    async with app.run_test() as pilot:
        # Initial state should be MarkdownStep
        assert isinstance(app.current_chapter.current_step, MarkdownStep)
        assert app.current_chapter.markdown_container.visible
        assert not app.current_chapter.code_display.visible

        # Check if the correct content is in the Markdown widget
        markdown_widget = pilot.app.query_one("#markdown")
        assert "# Header 1" in markdown_widget._markdown

        # Move to the next step (Code Step)
        await pilot.press("down")
        assert isinstance(app.current_chapter.current_step, Step)
        assert not app.current_chapter.markdown_container.visible
        assert app.current_chapter.code_display.visible

        # Move to the next step (Markdown Step)
        await pilot.press("down")
        assert isinstance(app.current_chapter.current_step, MarkdownStep)
        assert app.current_chapter.markdown_container.visible
        assert not app.current_chapter.code_display.visible
        markdown_widget = pilot.app.query_one("#markdown")
        assert "## Header 2" in markdown_widget.render()


@pytest.mark.asyncio
async def test_markdown_step_toggle_dim(markdown_chapter):
    """Test that toggle_dim doesn't affect MarkdownStep."""
    app = TuitorialApp([markdown_chapter])
    async with app.run_test() as pilot:
        # Initial state should be MarkdownStep
        assert app.current_chapter.markdown_container.visible
        assert not app.current_chapter.code_display.visible

        # Press toggle_dim key
        await pilot.press("d")

        # Ensure toggle_dim didn't affect MarkdownStep and code display is still not visible
        assert app.current_chapter.markdown_container.visible
        assert not app.current_chapter.code_display.visible
