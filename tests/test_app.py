# tests/test_app.py
import pytest

from tuitorial.app import Chapter, Step, TutorialApp
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
    app = TutorialApp([chapter])
    async with app.run_test():
        assert len(app.chapters) == 1
        assert app.chapters[0] == chapter
        assert app.current_chapter_index == 0


@pytest.mark.asyncio
async def test_next_focus(chapter):
    """Test next focus action."""
    app = TutorialApp([chapter])
    async with app.run_test() as pilot:
        # Initial state
        assert app.current_chapter.current_index == 0

        # Press down arrow
        await pilot.press("down")
        assert app.current_chapter.current_index == 1


@pytest.mark.asyncio
async def test_previous_focus(chapter):
    """Test previous focus action."""
    app = TutorialApp([chapter])
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
    app = TutorialApp([chapter])
    async with app.run_test() as pilot:
        # Move to last step
        chapter.current_index = len(chapter.steps) - 1

        # Press reset key
        await pilot.press("r")
        assert chapter.current_index == 0


@pytest.mark.asyncio
async def test_quit():
    """Test quit action."""
    app = TutorialApp([])
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
    app = TutorialApp([chapter])
    async with app.run_test():
        initial_description = app.query_one("#description").render()

        # Move to next step
        chapter.next_step()
        new_description = app.query_one("#description").render()

        assert initial_description != new_description


@pytest.mark.asyncio
async def test_current_step(chapter):
    """Test current_step property."""
    app = TutorialApp([chapter])
    async with app.run_test():
        assert chapter.current_step == chapter.steps[0]


@pytest.mark.asyncio
async def test_current_description(chapter):
    """Test current_description property."""
    app = TutorialApp([chapter])
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
    app = TutorialApp([chapter, chapter2])

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
    app = TutorialApp([chapter])
    async with app.run_test() as pilot:
        await pilot.press("d")
        assert not app.current_chapter.code_display.dim_background
        await pilot.press("d")
        assert app.current_chapter.code_display.dim_background
