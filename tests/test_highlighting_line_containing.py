"""Tests for the line_containing focus type."""

import pytest
from rich.style import Style

from tuitorial.highlighting import Focus
from tuitorial.widgets import CodeDisplay


@pytest.fixture
def multiline_code() -> str:
    return """def first():
    return 1

def second():
    return 2

def third():
    return 3"""


def test_line_containing_basic():
    """Test basic line containing functionality."""
    code = "line one\nline two\nline three"
    display = CodeDisplay(code)
    focus = Focus.line_containing("two", style="bold yellow")
    display.update_focuses([focus])
    result = display.highlight_code()

    # Get highlighted ranges
    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert len(highlights) == 1
    start, end = next(iter(highlights))
    assert code[start:end] == "line two\n"


def test_line_containing_with_surrounding_lines(multiline_code):
    """Test line containing with lines before and after."""
    display = CodeDisplay(multiline_code)
    focus = Focus.line_containing(
        "second",
        style="bold yellow",
        lines_before=1,
        lines_after=1,
    )
    display.update_focuses([focus])
    result = display.highlight_code()

    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert len(highlights) == 1
    start, end = next(iter(highlights))
    expected = "\ndef second():\n    return 2\n"
    assert multiline_code[start:end] == expected


def test_line_containing_regex():
    """Test line containing with regex pattern."""
    code = "abc123\ndef456\nghi789"
    display = CodeDisplay(code)
    focus = Focus.line_containing(r"\d+", style="bold yellow", regex=True)
    display.update_focuses([focus])
    result = display.highlight_code()

    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert len(highlights) == 3  # Should match all three lines


def test_line_containing_match_index(multiline_code):
    """Test line containing with specific match index."""
    display = CodeDisplay(multiline_code)
    focus = Focus.line_containing(
        "def",
        style="bold yellow",
        match_index=1,  # Get second function
    )
    display.update_focuses([focus])
    result = display.highlight_code()

    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert len(highlights) == 1
    start, end = next(iter(highlights))
    assert multiline_code[start:end] == "def second():\n"


def test_line_containing_invalid_match_index(multiline_code):
    """Test line containing with invalid match index."""
    display = CodeDisplay(multiline_code)
    focus = Focus.line_containing(
        "def",
        style="bold yellow",
        match_index=10,  # Invalid index
    )
    display.update_focuses([focus])
    result = display.highlight_code()

    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert len(highlights) == 0  # Should find no matches


def test_line_containing_style_parsing():
    """Test line containing with different style specifications."""
    code = "test line"
    display = CodeDisplay(code)

    # Test with string style
    focus1 = Focus.line_containing("test", style="bold yellow")
    display.update_focuses([focus1])
    result1 = display.highlight_code()

    # Test with Style object
    focus2 = Focus.line_containing("test", style=Style(bold=True, color="yellow"))
    display.update_focuses([focus2])
    result2 = display.highlight_code()

    # Results should be identical
    assert result1 == result2


def test_line_containing_at_boundaries():
    """Test line containing at text boundaries."""
    code = "first line\nmiddle line\nlast line"
    display = CodeDisplay(code)

    # Test first line
    focus = Focus.line_containing("first", style="bold yellow")
    display.update_focuses([focus])
    result = display.highlight_code()
    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert (0, len("first line\n")) in highlights

    # Test last line
    focus = Focus.line_containing("last", style="bold yellow")
    display.update_focuses([focus])
    result = display.highlight_code()
    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert (code.rfind("last"), len(code)) in highlights


def test_line_containing_multiple_matches_same_line():
    """Test line containing with multiple matches in the same line."""
    code = "test test test\nother line"
    display = CodeDisplay(code)
    focus = Focus.line_containing("test", style="bold yellow")
    display.update_focuses([focus])
    result = display.highlight_code()

    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert len(highlights) == 1  # Should only highlight the line once


def test_line_containing_empty_pattern():
    """Test line containing with empty pattern."""
    code = "test line"
    display = CodeDisplay(code)
    focus = Focus.line_containing("", style="bold yellow")
    display.update_focuses([focus])
    result = display.highlight_code()

    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert len(highlights) == 1  # Should match every line


def test_line_containing_no_matches():
    """Test line containing with pattern that doesn't match."""
    code = "test line\nother line"
    display = CodeDisplay(code)
    focus = Focus.line_containing("nonexistent", style="bold yellow")
    display.update_focuses([focus])
    result = display.highlight_code()

    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert len(highlights) == 0


def test_line_containing_with_yaml_parsing(tmp_path):
    """Test line containing focus type through YAML parsing."""
    from tuitorial.parse_yaml import parse_yaml_config

    yaml_content = """
    chapters:
    - title: "Test Chapter"
      code: |
        def first():
            return 1
        def second():
            return 2
      steps:
      - description: "Test step"
        focus:
        - type: line_containing
          pattern: "def"
          style: "bold yellow"
          lines_after: 1
          match_index: 0
          regex: false
    """

    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)

    chapters, _ = parse_yaml_config(str(yaml_file))
    assert len(chapters) == 1
    assert len(chapters[0].steps) == 1

    focus = chapters[0].steps[0].focuses[0]
    assert focus.type.name == "LINE_CONTAINING"
    assert focus.pattern == "def"
    assert focus.style == Style.parse("bold yellow")
    assert focus.extra["lines_after"] == 1
    assert focus.extra["match_index"] == 0
