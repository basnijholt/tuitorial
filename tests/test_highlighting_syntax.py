"""Tests for the syntax highlighting focus type."""

import pytest
from rich.text import Text

from tuitorial.highlighting import Focus, FocusType
from tuitorial.widgets import CodeDisplay


@pytest.fixture
def python_code() -> str:
    return """def example():
    x = 1  # comment
    return x + 2

def another():
    pass"""


def test_syntax_basic(python_code):
    """Test basic syntax highlighting."""
    display = CodeDisplay(python_code)
    focus = Focus.syntax()
    display.update_focuses([focus])
    result = display.highlight_code()

    # Should return a Text object
    assert isinstance(result, Text)
    # Should contain syntax highlighted code
    assert "def" in result.plain  # Basic content check


def test_syntax_with_theme(python_code):
    """Test syntax highlighting with specific theme."""
    display = CodeDisplay(python_code)
    focus = Focus.syntax(theme="monokai")
    display.update_focuses([focus])
    result = display.highlight_code()

    # Check that styling was applied
    styled_ranges = [style for _, _, style in result.spans if style]
    assert styled_ranges  # Should have some styled ranges


def test_syntax_with_line_numbers(python_code):
    """Test syntax highlighting with line numbers."""
    display = CodeDisplay(python_code)
    focus = Focus.syntax(line_numbers=True)
    display.update_focuses([focus])
    result = display.highlight_code()

    # Should contain line numbers in the output
    assert "1" in result.plain
    assert "2" in result.plain


def test_syntax_with_line_range(python_code):
    """Test syntax highlighting with line range."""
    display = CodeDisplay(python_code)
    focus = Focus.syntax(start_line=0, end_line=3)
    display.update_focuses([focus])
    result = display.highlight_code()

    # Should only contain the first function
    assert "def example" in result.plain
    assert "def another" not in result.plain


def test_syntax_with_different_lexer():
    """Test syntax highlighting with different language."""
    code = "SELECT * FROM table;"
    display = CodeDisplay(code)
    focus = Focus.syntax(lexer="sql")
    display.update_focuses([focus])
    result = display.highlight_code()

    assert isinstance(result, Text)
    assert "SELECT" in result.plain


def test_syntax_focus_properties():
    """Test syntax focus object properties."""
    focus = Focus.syntax(
        lexer="python",
        theme="monokai",
        line_numbers=True,
        start_line=1,
        end_line=3,
    )

    assert focus.type == FocusType.SYNTAX
    assert isinstance(focus.extra, dict)
    assert focus.extra["lexer"] == "python"
    assert focus.extra["theme"] == "monokai"
    assert focus.extra["line_numbers"] is True
    assert focus.extra["start_line"] == 1
    assert focus.extra["end_line"] == 3


def test_syntax_with_invalid_range(python_code):
    """Test syntax highlighting with invalid line range."""
    display = CodeDisplay(python_code)
    focus = Focus.syntax(start_line=10, end_line=20)  # Beyond code length
    display.update_focuses([focus])
    result = display.highlight_code()

    # Should return empty but valid Text object
    assert isinstance(result, Text)
    assert not result.plain.strip()


def test_multiple_syntax_focuses(python_code):
    """Test that only first syntax focus is used."""
    display = CodeDisplay(python_code)
    focus1 = Focus.syntax(theme="monokai")
    focus2 = Focus.syntax(theme="default")
    display.update_focuses([focus1, focus2])
    result1 = display.highlight_code()

    display.update_focuses([focus2])
    result2 = display.highlight_code()

    # Results should be different as only first focus is used
    assert result1.plain == result2.plain  # Content should be same
    assert result1.spans != result2.spans  # But styling should differ


def test_syntax_with_yaml_parsing(tmp_path):
    """Test syntax focus type through YAML parsing."""
    from tuitorial.parse_yaml import parse_yaml_config

    yaml_content = """
    chapters:
    - title: "Test Chapter"
      code: |
        def example():
            return 42
      steps:
      - description: "Test step"
        focus:
        - type: syntax
          lexer: "python"
          theme: "monokai"
          line_numbers: true
          start_line: 0
          end_line: 2
    """

    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)

    chapters, _ = parse_yaml_config(str(yaml_file))
    assert len(chapters) == 1
    assert len(chapters[0].steps) == 1

    focus = chapters[0].steps[0].focuses[0]
    assert focus.type == FocusType.SYNTAX
    assert focus.extra["lexer"] == "python"
    assert focus.extra["theme"] == "monokai"
    assert focus.extra["line_numbers"] is True
    assert focus.extra["start_line"] == 0
    assert focus.extra["end_line"] == 2


def test_mixing_syntax_with_other_focuses(python_code):
    """Test that syntax focus takes precedence over other focuses."""
    display = CodeDisplay(python_code)
    focuses = [
        Focus.literal("def", style="bold red"),
        Focus.syntax(theme="monokai"),
    ]
    display.update_focuses(focuses)
    result = display.highlight_code()

    # Should use syntax highlighting, not literal focus
    assert isinstance(result, Text)
    # Compare normalized line endings
    assert result.plain.rstrip("\n") == python_code.rstrip("\n")
