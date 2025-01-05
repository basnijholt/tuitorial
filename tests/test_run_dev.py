from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tuitorial.parse_yaml import TuitorialApp, parse_yaml_config, reload_app


@pytest.fixture
def sample_yaml_file(tmp_path):
    """Fixture to create a sample YAML file for testing."""
    yaml_content = """
    chapters:
      - title: "Chapter 1"
        code: |
          print("Hello")
        steps:
          - description: "First step"
            focus:
              - type: literal
                text: "print"
                style: "bold blue"
    """
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)
    return str(yaml_file)


@pytest.fixture
def mock_tuitorial_app():
    """Fixture to mock TuitorialApp."""
    mock_app = MagicMock(spec=TuitorialApp)
    mock_app.current_chapter_index = 0
    mock_app.current_chapter.current_index = 0
    return mock_app


def test_parse_yaml_config_valid(sample_yaml_file):
    """Test parsing a valid YAML config."""
    chapters, title_slide = parse_yaml_config(sample_yaml_file)
    assert len(chapters) == 1
    assert chapters[0].title == "Chapter 1"
    assert chapters[0].steps[0].description == "First step"


@pytest.mark.asyncio
async def test_reload_app_updates_chapters(sample_yaml_file, mock_tuitorial_app):
    """Test that reload_app updates the app with new chapters and preserves state."""
    # Mock the initial state
    mock_tuitorial_app.current_chapter_index = 1
    mock_tuitorial_app.current_chapter.current_index = 2
    mock_tuitorial_app.recompose = AsyncMock()
    mock_tuitorial_app.set_chapter = AsyncMock()
    mock_tuitorial_app.set_step = AsyncMock()

    # Mock parse_yaml_config to return new chapters and title slide
    new_chapters = ["new", "chapters"]
    new_title_slide = "new title slide"
    with patch(
        "tuitorial.parse_yaml.parse_yaml_config",
        return_value=(new_chapters, new_title_slide),
    ):
        await reload_app(mock_tuitorial_app, sample_yaml_file)

        # Assertions
        assert mock_tuitorial_app.chapters == new_chapters
        assert mock_tuitorial_app.title_slide == new_title_slide
        mock_tuitorial_app.recompose.assert_awaited_once()
        mock_tuitorial_app.set_chapter.assert_awaited_once_with(
            1,
            nearest=True,
        )  # Check if preserved
        mock_tuitorial_app.set_step.assert_awaited_once_with(2)  # Check if preserved
