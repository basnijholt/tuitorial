# tests/test_highlighting_between.py

from rich.style import Style

from tuitorial.highlighting import Focus
from tuitorial.widgets import CodeDisplay


def test_between_focus():
    """Test the between focus type."""
    code = """
def start_here():
    print("middle content")
    more_code()
end_here
"""
    # Test inclusive highlighting
    display = CodeDisplay(code)
    focus = Focus.between(
        "start_here",
        "end_here",
        style=Style(color="blue", bold=True),
        inclusive=True,
    )
    display.update_focuses([focus])
    result = display.highlight_code()

    # Get highlighted ranges
    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}

    # Check that the correct range is highlighted
    start_idx = code.find("start_here")
    end_idx = code.find("end_here") + len("end_here")
    assert (start_idx, end_idx) in highlights


def test_between_focus_exclusive():
    """Test the between focus type with exclusive bounds."""
    code = "START content END"
    display = CodeDisplay(code)
    focus = Focus.between(
        "START",
        "END",
        style=Style(color="blue", bold=True),
        inclusive=False,
    )
    display.update_focuses([focus])
    result = display.highlight_code()

    highlights = {code[start:end] for start, end, style in result.spans if style and not style.dim}

    assert " content " in highlights
    assert "START" not in highlights
    assert "END" not in highlights


def test_between_focus_multiline():
    """Test the between focus type with multiline content."""
    code = """
START
line 1
line 2
END
"""
    display = CodeDisplay(code)
    focus = Focus.between(
        "START",
        "END",
        style=Style(color="blue", bold=True),
        inclusive=True,
        multiline=True,
    )
    display.update_focuses([focus])
    result = display.highlight_code()

    # Get highlighted text
    highlighted_text = ""
    for start, end, style in result.spans:
        if style and not style.dim:
            highlighted_text = code[start:end]

    assert "START" in highlighted_text
    assert "line 1" in highlighted_text
    assert "line 2" in highlighted_text
    assert "END" in highlighted_text


def test_between_focus_multiple_matches():
    """Test the between focus type with multiple matches."""
    code = """
START
content1
END
other stuff
START
content2
END
"""
    # Test matching all occurrences
    display = CodeDisplay(code)
    focus = Focus.between(
        "START",
        "END",
        style=Style(color="blue", bold=True),
        inclusive=True,
    )
    display.update_focuses([focus])
    result = display.highlight_code()

    highlights = {code[start:end] for start, end, style in result.spans if style and not style.dim}

    assert len(highlights) == 2  # Should find both matches
    assert any("content1" in h for h in highlights)
    assert any("content2" in h for h in highlights)


def test_between_focus_specific_match():
    """Test the between focus type with specific match index."""
    code = """
START
content1
END
other stuff
START
content2
END
"""
    # Test matching only the second occurrence
    display = CodeDisplay(code)
    focus = Focus.between(
        "START",
        "END",
        style=Style(color="blue", bold=True),
        inclusive=True,
        match_index=1,  # Get second match
    )
    display.update_focuses([focus])
    result = display.highlight_code()

    highlights = {code[start:end] for start, end, style in result.spans if style and not style.dim}

    assert len(highlights) == 1  # Should find only one match
    assert any("content2" in h for h in highlights)
    assert not any("content1" in h for h in highlights)


def test_between_focus_greedy():
    """Test the between focus type with greedy matching."""
    code = """
START
content1
END
middle
START
content2
END
"""
    # Test greedy vs non-greedy matching
    display = CodeDisplay(code)

    # Non greedy (default)
    focus1 = Focus.between(
        "START",
        "END",
        style=Style(color="blue", bold=True),
        inclusive=True,
        greedy=False,
    )
    display.update_focuses([focus1])
    result1 = display.highlight_code()
    highlights1 = {
        code[start:end] for start, end, style in result1.spans if style and not style.dim
    }

    # Greedy
    focus2 = Focus.between(
        "START",
        "END",
        style=Style(color="blue", bold=True),
        inclusive=True,
        greedy=True,
    )
    display.update_focuses([focus2])
    result2 = display.highlight_code()
    highlights2 = {
        code[start:end] for start, end, style in result2.spans if style and not style.dim
    }

    # Non-greedy should find two separate matches
    assert len(highlights1) == 2
    # Greedy should find one match containing everything between first START and last END
    assert len(highlights2) == 1
    assert any("middle" in h for h in highlights2)
