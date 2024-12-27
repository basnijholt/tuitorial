"""Tests for markdown focus functionality."""

import pytest
from textual.widgets import Markdown

from tuitorial.highlighting import Focus, FocusType
from tuitorial.widgets import ContentContainer, Step


def test_markdown_focus_creation():
    """Test creation of markdown focus."""
    focus = Focus.markdown()
    assert focus.type == FocusType.MARKDOWN
    assert focus.pattern == ""  # Pattern is not used for markdown
    assert focus.style == ""  # Style is not used for markdown
    assert focus.extra is None  # No extra options needed for markdown


@pytest.mark.asyncio
async def test_markdown_display(app_runner):
    """Test displaying markdown content."""
    markdown_text = """# Header

Some **bold** text and *italic* text.

- List item 1
- List item 2
"""
    container = ContentContainer(markdown_text)

    # Test with markdown focus
    await container.update_display(Step("", [Focus.markdown()]))

    # Check that markdown widget is visible and code is hidden
    assert container.markdown.styles.display == "block"
    assert container.code_display.styles.display == "none"

    # Check that the markdown content is set correctly
    assert isinstance(container.markdown, Markdown)
    assert container.markdown._markdown == markdown_text


@pytest.mark.asyncio
async def test_mixed_focus_types(app_runner):
    """Test that markdown focus takes precedence over other focus types."""
    content = "# Test Content"
    container = ContentContainer(content)

    focuses = [
        Focus.literal("Test", style="bold red"),
        Focus.markdown(),
        Focus.syntax(),
    ]

    await container.update_display(Step("", focuses))

    # Markdown should be shown, code hidden
    assert container.markdown.styles.display == "block"
    assert container.code_display.styles.display == "none"


@pytest.mark.asyncio
async def test_switch_between_markdown_and_code(app_runner):
    """Test switching between markdown and code display."""
    content = "# Test Content"
    container = ContentContainer(content)

    # Start with markdown
    await container.update_display(step=Step("", [Focus.markdown()]))
    assert container.markdown.styles.display == "block"
    assert container.code_display.styles.display == "none"

    # Switch to code
    await container.update_display(step=Step("", [Focus.literal("Test")]))
    assert container.markdown.styles.display == "none"
    assert container.code_display.styles.display == "block"

    # Switch back to markdown
    await container.update_display(step=Step("", [Focus.markdown()]))
    assert container.markdown.styles.display == "block"
    assert container.code_display.styles.display == "none"


@pytest.fixture
async def app_runner():
    """Fixture for running async tests."""
    from textual.app import App

    class TestApp(App):
        pass

    async with TestApp().run_test() as pilot:
        yield pilot
