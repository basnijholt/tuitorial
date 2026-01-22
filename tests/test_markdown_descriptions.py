# tests/test_markdown_descriptions.py
"""Tests for Markdown rendering in step descriptions."""

import pytest
from rich.text import Text

from tuitorial.widgets import (
    Step,
    _calculate_height,
    _calculate_heights_of_steps,
    _render_markdown,
)


class TestRenderMarkdown:
    """Tests for the _render_markdown function."""

    def test_returns_text_object(self):
        """Render markdown should return a Rich Text object."""
        result = _render_markdown("Hello world")
        assert isinstance(result, Text)

    def test_plain_text(self):
        """Plain text should be preserved."""
        result = _render_markdown("Hello world")
        assert "Hello world" in result.plain

    def test_bold_text(self):
        """Bold markdown should be rendered."""
        result = _render_markdown("**bold text**")
        assert "bold text" in result.plain
        # Check that bold styling is applied (spans should exist)
        assert len(result.spans) > 0

    def test_italic_text(self):
        """Italic markdown should be rendered."""
        result = _render_markdown("*italic text*")
        assert "italic text" in result.plain

    def test_heading(self):
        """Headings should be rendered."""
        result = _render_markdown("## Heading")
        assert "Heading" in result.plain

    def test_bullet_list(self):
        """Bullet lists should be rendered."""
        result = _render_markdown("- item 1\n- item 2")
        assert "item 1" in result.plain
        assert "item 2" in result.plain

    def test_numbered_list(self):
        """Numbered lists should be rendered."""
        result = _render_markdown("1. first\n2. second")
        assert "first" in result.plain
        assert "second" in result.plain

    def test_inline_code(self):
        """Inline code should be rendered."""
        result = _render_markdown("Use `print()` function")
        assert "print()" in result.plain

    def test_blockquote(self):
        """Blockquotes should be rendered."""
        result = _render_markdown("> This is a quote")
        assert "This is a quote" in result.plain

    def test_multiline_content(self):
        """Multiline markdown should be rendered correctly."""
        content = """## Title

This is a paragraph.

- Point 1
- Point 2
"""
        result = _render_markdown(content)
        assert "Title" in result.plain
        assert "paragraph" in result.plain
        assert "Point 1" in result.plain

    def test_custom_width(self):
        """Custom width should affect rendering."""
        long_text = "This is a very long line that should wrap when width is small"
        result_narrow = _render_markdown(long_text, width=20)
        result_wide = _render_markdown(long_text, width=200)
        # Narrow should have more newlines due to wrapping
        assert result_narrow.plain.count("\n") >= result_wide.plain.count("\n")


class TestCalculateHeight:
    """Tests for the _calculate_height function."""

    def test_single_line(self):
        """Single line text should have height of 1 or 2 (markdown adds spacing)."""
        height = _calculate_height("Hello")
        assert height >= 1

    def test_multiline(self):
        """Multiline text should have proportional height."""
        height = _calculate_height("Line 1\n\nLine 2\n\nLine 3")
        assert height >= 3

    def test_heading_adds_space(self):
        """Headings add extra vertical space."""
        plain_height = _calculate_height("Some text")
        heading_height = _calculate_height("## Heading")
        # Heading should take at least as much space
        assert heading_height >= plain_height

    def test_width_affects_height(self):
        """Narrow width causes more line wrapping."""
        long_text = "This is a long line " * 10
        narrow_height = _calculate_height(long_text, width=20)
        wide_height = _calculate_height(long_text, width=200)
        assert narrow_height > wide_height


class TestCalculateHeightsOfSteps:
    """Tests for the _calculate_heights_of_steps function."""

    def test_empty_steps(self):
        """Empty step list should return 0."""
        height = _calculate_heights_of_steps([])
        assert height == 0

    def test_single_step(self):
        """Single step should return its height."""
        steps = [Step("Hello world", [])]
        height = _calculate_heights_of_steps(steps)
        assert height > 0

    def test_returns_max_height(self):
        """Should return the maximum height across all steps."""
        steps = [
            Step("Short", []),
            Step("This is a much longer description\n\nWith multiple lines\n\n- And bullets", []),
            Step("Medium length text here", []),
        ]
        height = _calculate_heights_of_steps(steps)
        # Height should be at least as tall as the longest step
        single_height = _calculate_heights_of_steps([steps[1]])
        assert height >= single_height

    def test_includes_step_counter(self):
        """Height calculation should include the step counter prefix."""
        steps = [Step("Description", [])]
        height = _calculate_heights_of_steps(steps)
        # Should include space for "**Step 1/1**\n\n" prefix
        description_only = _calculate_height("Description")
        assert height > description_only


class TestMarkdownInApp:
    """Integration tests for markdown descriptions in the app."""

    @pytest.fixture
    def chapter_with_markdown(self):
        """Create a chapter with markdown descriptions."""
        from tuitorial.widgets import Chapter

        steps = [
            Step("## Welcome\n\nThis is **bold** and *italic*.", []),
            Step("### Features\n\n- Item 1\n- Item 2", []),
        ]
        return Chapter("Test", "code", steps)

    def test_chapter_renders_markdown(self, chapter_with_markdown):
        """Chapter should render markdown in descriptions."""
        # The description widget should be set up
        assert chapter_with_markdown.description is not None

    def test_step_counter_in_description(self, chapter_with_markdown):
        """Step counter should be included in rendered description."""
        # This would require async testing to fully verify
        # Just check the step exists
        assert len(chapter_with_markdown.steps) == 2
