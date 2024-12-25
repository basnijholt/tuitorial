import pytest
from rich.style import Style

from tuitorial import Chapter, Focus
from tuitorial.helpers import create_bullet_point_chapter


def test_create_bullet_point_chapter_basic():
    """Test basic creation of a bullet point chapter."""
    title = "Test Chapter"
    bullet_points = ["Point 1", "Point 2"]
    chapter = create_bullet_point_chapter(title, bullet_points)

    assert isinstance(chapter, Chapter)
    assert chapter.title == title
    assert len(chapter.steps) == 2
    assert chapter.steps[0].description == ""
    assert chapter.steps[1].description == ""
    assert chapter.code == "- Point 1\n- Point 2"

    # Check focus type and style
    for i, step in enumerate(chapter.steps):
        assert len(step.focuses) == 1
        focus = step.focuses[0]
        assert isinstance(focus, Focus)
        assert focus.type == focus.type.LINE
        assert focus.pattern == i
        assert focus.style == Style(color="cyan", bold=True)


def test_create_bullet_point_chapter_with_extras():
    """Test creating a chapter with extra content for each step."""
    title = "Test Chapter"
    bullet_points = ["Point 1", "Point 2"]
    extras = ["Extra 1", "Extra 2"]
    chapter = create_bullet_point_chapter(title, bullet_points, extras=extras)

    assert isinstance(chapter, Chapter)
    assert chapter.title == title
    assert len(chapter.steps) == 2
    assert chapter.steps[0].description == "Extra 1"
    assert chapter.steps[1].description == "Extra 2"
    assert chapter.code == "- Point 1\n- Point 2"


def test_create_bullet_point_chapter_custom_style():
    """Test using a custom style for highlighting."""
    title = "Test Chapter"
    bullet_points = ["Point 1", "Point 2"]
    custom_style = Style(color="red", italic=True)
    chapter = create_bullet_point_chapter(title, bullet_points, style=custom_style)

    for step in chapter.steps:
        focus = step.focuses[0]
        assert focus.style == custom_style


def test_create_bullet_point_chapter_invalid_extras():
    """Test that an error is raised when extras length doesn't match."""
    title = "Test Chapter"
    bullet_points = ["Point 1", "Point 2"]
    extras = ["Extra 1"]  # Incorrect length

    with pytest.raises(
        ValueError,
        match="The number of extras must match the number of bullet points.",
    ):
        create_bullet_point_chapter(title, bullet_points, extras=extras)


def test_create_bullet_point_numbered():
    """Test creating a numbered bullet point chapter."""
    title = "Test Chapter"
    bullet_points = ["Point 1", "Point 2"]
    chapter = create_bullet_point_chapter(title, bullet_points, marker="1.")

    assert chapter.code == "1. Point 1\n2. Point 2"
    for i, step in enumerate(chapter.steps):
        focus = step.focuses[0]
        assert focus.pattern == i
