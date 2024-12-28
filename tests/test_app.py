# tests/test_app.py
from pathlib import Path

import PIL
import pytest
from pyfiglet import Figlet
from rich.text import Text

from tuitorial import Chapter, ImageStep, Step, TitleSlide, TuitorialApp
from tuitorial.highlighting import Focus


@pytest.fixture
def example_code():
    return "def test():\n    pass\n"


@pytest.fixture
def tutorial_steps():
    return [
        Step("Step 1", [Focus.literal("def")]),
        Step("Step 2", [Focus.literal("pass")]),
    ]


@pytest.fixture
def chapter(example_code, tutorial_steps):
    return Chapter("Test Chapter", example_code, tutorial_steps)


@pytest.mark.asyncio
async def test_app_init(chapter):
    """Test app initialization."""
    app = TuitorialApp([chapter])
    async with app.run_test():
        assert len(app.chapters) == 1
        assert app.chapters[0] == chapter
        assert app.current_chapter_index == 0


@pytest.mark.asyncio
async def test_next_focus(chapter):
    """Test next focus action."""
    app = TuitorialApp([chapter])
    async with app.run_test() as pilot:
        # Initial state
        assert app.current_chapter.current_index == 0

        # Press down arrow
        await pilot.press("down")
        assert app.current_chapter.current_index == 1


@pytest.mark.asyncio
async def test_previous_focus(chapter):
    """Test previous focus action."""
    app = TuitorialApp([chapter])
    async with app.run_test() as pilot:
        # Initial state
        assert app.current_chapter.current_index == 0

        # Move to last step
        app.current_chapter.current_index = len(chapter.steps) - 1
        assert app.current_chapter.current_index == 1

        # Press up arrow
        await pilot.press("up")
        assert app.current_chapter.current_index == 0


@pytest.mark.asyncio
async def test_reset_focus(chapter):
    """Test reset focus action."""
    app = TuitorialApp([chapter])
    async with app.run_test() as pilot:
        # Move to last step
        chapter.current_index = len(chapter.steps) - 1

        # Press reset key
        await pilot.press("r")
        assert chapter.current_index == 0


@pytest.mark.asyncio
async def test_quit():
    """Test quit action."""
    app = TuitorialApp([])
    async with app.run_test() as pilot:
        # Create a task to press 'q'
        async def press_q():
            await pilot.press("q")

        # Run the press_q task and expect the app to exit
        await press_q()
        assert not app.is_running


@pytest.mark.asyncio
async def test_update_display(chapter):
    """Test display updates."""
    app = TuitorialApp([chapter])
    async with app.run_test():
        initial_description = app.query_one("#description").render()

        # Move to next step
        await chapter.next_step()
        new_description = app.query_one("#description").render()

        assert initial_description != new_description


@pytest.mark.asyncio
async def test_current_step(chapter):
    """Test current_step property."""
    app = TuitorialApp([chapter])
    async with app.run_test():
        assert chapter.current_step == chapter.steps[0]


@pytest.mark.asyncio
async def test_current_description(chapter):
    """Test current_description property."""
    app = TuitorialApp([chapter])
    async with app.run_test():
        assert chapter.current_step.description == chapter.steps[0].description


@pytest.mark.asyncio
async def test_switch_chapters(chapter, example_code):
    """Test switching between chapters."""
    # Create a second chapter
    chapter2_steps = [
        Step("Step 1 Chapter 2", [Focus.literal("test")]),
    ]
    chapter2 = Chapter("Test Chapter 2", example_code, chapter2_steps)
    app = TuitorialApp([chapter, chapter2])

    async with app.run_test() as pilot:
        # Ensure the tabs are mounted
        await pilot.press("right")
        assert app.current_chapter.title == chapter2.title
        assert app.current_chapter_index == 1
        await pilot.press("right")
        assert app.current_chapter.title == chapter.title
        assert app.current_chapter_index == 0


@pytest.mark.asyncio
async def test_toggle_dim(chapter) -> None:
    """Test toggling dim."""
    app = TuitorialApp([chapter])
    async with app.run_test() as pilot:
        await pilot.press("d")
        assert not app.current_chapter.content.code_display.dim_background
        await pilot.press("d")
        assert app.current_chapter.content.code_display.dim_background


@pytest.fixture
def image_path(tmp_path: Path) -> Path:
    im = PIL.Image.new(mode="RGB", size=(200, 200))
    filename = tmp_path / "test_image.png"
    im.save(filename)
    return filename


@pytest.mark.asyncio
async def test_image_step(example_code, image_path: Path):
    """Test ImageStep functionality."""
    steps: list[ImageStep | Step] = [
        ImageStep("Image Step", image_path),
        Step("Code Step", [Focus.literal("def")]),
    ]
    chapter = Chapter("Test Chapter", example_code, steps)
    app = TuitorialApp([chapter])

    async with app.run_test() as pilot:
        # Initial state should be ImageStep
        assert isinstance(app.current_chapter.current_step, ImageStep)
        content = app.current_chapter.content
        assert content.image_container.styles.display == "block"
        assert content.code_display.styles.display == "none"
        assert content.markdown.styles.display == "none"

        # Move to next step (Code Step)
        await pilot.press("down")
        assert isinstance(app.current_chapter.current_step, Step)
        assert content.image_container.styles.display == "none"
        assert content.code_display.styles.display == "block"
        assert content.markdown.styles.display == "none"

        # Move back to ImageStep
        await pilot.press("up")
        assert isinstance(app.current_chapter.current_step, ImageStep)
        assert content.image_container.styles.display == "block"
        assert content.code_display.styles.display == "none"


@pytest.mark.asyncio
async def test_toggle_dim_image_step(example_code: str, image_path: Path):
    """Test that toggle_dim doesn't affect ImageStep."""
    steps: list[ImageStep | Step] = [
        ImageStep("Image Step", image_path),
        Step("Code Step", [Focus.literal("def")]),
    ]
    chapter = Chapter("Test Chapter", example_code, steps)
    app = TuitorialApp([chapter])

    async with app.run_test() as pilot:
        # Initial state should be ImageStep
        content = app.current_chapter.content
        assert content.image_container.styles.display == "block"
        assert content.code_display.styles.display == "none"

        # Press toggle_dim key
        await pilot.press("d")

        # Ensure toggle_dim didn't affect ImageStep and code display is still not visible
        assert content.image_container.styles.display == "block"
        assert content.code_display.styles.display == "none"


@pytest.mark.asyncio
async def test_image_step_dimensions_and_alignment(example_code, image_path: Path):
    """Test setting width, height, and alignment for ImageStep."""
    steps: list[ImageStep | Step] = [
        ImageStep("Fixed Size", image_path, width=100, height=50, halign="left"),
        ImageStep("Percentage Width", image_path, width="50%", height=100, halign="right"),
    ]
    chapter = Chapter("Test Chapter", example_code, steps)
    app = TuitorialApp([chapter])

    async with app.run_test() as pilot:
        # Check first ImageStep (fixed size)
        image_widget = app.query_one("#image")
        assert image_widget.styles.width.value == 100
        assert image_widget.styles.height.value == 50
        assert image_widget.styles.align_horizontal == "left"

        # Move to the next ImageStep (percentage width)
        await pilot.press("down")

        # Check second ImageStep (percentage width)
        image_widget = app.query_one("#image")
        assert image_widget.styles.width.value == 50
        assert image_widget.styles.height.value == 100
        assert image_widget.styles.align_horizontal == "right"


@pytest.mark.asyncio
async def test_title_slide_dimensions():
    """Test that the TitleSlide sets the correct dimensions."""
    title = "My Title"
    subtitle = "My Subtitle"
    font = "slant"  # Use a known, standard font
    app = TuitorialApp([], title_slide=TitleSlide(title, subtitle, font=font))

    async with app.run_test():
        title_slide = app.query_one("#title-slide", TitleSlide)

        # Calculate expected dimensions based on content and font
        f = Figlet(font=font)
        ascii_art = f.renderText(title).splitlines()
        max_line_length = max(len(line) for line in ascii_art)
        width = max_line_length + 10  # Add padding
        height = len(ascii_art) + 2  # Add lines for spacing and subtitle (if present)

        # Check if subtitle adds to height
        if subtitle:
            console = title_slide.app.console
            subtitle_text = Text.from_markup(subtitle)
            wrapped_subtitle = subtitle_text.wrap(console, width=width)
            height += len(wrapped_subtitle) + 1  # Extra line for spacing

        # Check if the calculated dimensions match the actual dimensions
        assert title_slide.styles.width.value == pytest.approx(width, 1)
        assert title_slide.styles.height.value == pytest.approx(height, 1)


@pytest.mark.asyncio
async def test_switch_from_title_slide():
    """Test switching from the title slide to a chapter."""
    title_slide = TitleSlide("Title", "Subtitle")
    chapter = Chapter("Chapter 1", "code", [Step("Step 1", [Focus.literal("code")])])
    app = TuitorialApp([chapter], title_slide=title_slide)

    async with app.run_test() as pilot:
        # Initially, the title slide should be active
        assert app.current_chapter_index == -1

        # Switch to the next tab (chapter)
        await pilot.press("right")

        # Check that the chapter is now active
        assert app.current_chapter_index == 0
        assert app.current_chapter.title == "Chapter 1"
