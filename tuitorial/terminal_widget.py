"""Terminal widget used for terminal-focused tutorial steps."""

from __future__ import annotations

import asyncio
import fcntl
import os
import pty
import shlex
import struct
import termios
from collections.abc import Mapping, Sequence
from typing import Any

import pyte
from rich.style import Style
from rich.text import Text
from textual import events
from textual.widget import Widget

_DEFAULT_COLUMNS = 80
_DEFAULT_ROWS = 24


def _normalise_command(command: Sequence[str] | str | None) -> list[str]:
    """Return a list of arguments for the terminal subprocess."""
    if command is None:
        shell = os.environ.get("SHELL") or "/bin/bash"
        return [shell, "-i"]

    if isinstance(command, str):
        # Respect shell quoted strings.
        return shlex.split(command)

    return [str(part) for part in command]


def _merged_env(custom_env: Mapping[str, str] | None) -> dict[str, str]:
    """Build the environment for the spawned shell."""
    env = dict(os.environ)
    env.setdefault("TERM", "xterm-256color")
    if custom_env:
        env.update({str(key): str(value) for key, value in custom_env.items()})
    return env


class TerminalWidget(Widget, can_focus=True):
    """A lightweight terminal emulator based on ``pyte``."""

    DEFAULT_CSS = """
    TerminalWidget {
        height: 1fr;
        background: $surface;
        color: $text;
    }
    """

    def __init__(
        self,
        command: Sequence[str] | str | None = None,
        *,
        cwd: str | os.PathLike[str] | None = None,
        env: Mapping[str, str] | None = None,
        id: str | None = None,
        classes: str | None = None,
        name: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes, name=name)
        self._command = _normalise_command(command)
        self._cwd = os.fspath(cwd) if cwd is not None else None
        self._env = _merged_env(env)

        self._screen = pyte.Screen(_DEFAULT_COLUMNS, _DEFAULT_ROWS)
        self._stream = pyte.Stream(self._screen)

        self._loop: asyncio.AbstractEventLoop | None = None
        self._master_fd: int | None = None
        self._reader_registered = False
        self._process: asyncio.subprocess.Process | None = None
        self._closed_message = Text()

    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------
    async def on_mount(self) -> None:
        await self._start_terminal()

    async def on_unmount(self) -> None:
        await self._stop_terminal()

    async def _start_terminal(self) -> None:
        if self._process is not None:
            return

        master_fd, slave_fd = pty.openpty()
        self._master_fd = master_fd
        os.set_blocking(master_fd, False)

        self._loop = asyncio.get_running_loop()
        self._process = await asyncio.create_subprocess_exec(
            *self._command,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            cwd=self._cwd,
            env=self._env,
            start_new_session=True,
        )
        os.close(slave_fd)

        self._register_reader()
        self._apply_current_size()

    async def _stop_terminal(self) -> None:
        if self._reader_registered and self._loop and self._master_fd is not None:
            self._loop.remove_reader(self._master_fd)
            self._reader_registered = False

        if self._process is not None:
            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=2)
            except ProcessLookupError:
                pass
            except asyncio.TimeoutError:
                self._process.kill()
                await self._process.wait()

        if self._master_fd is not None:
            try:
                os.close(self._master_fd)
            except OSError:
                pass
        self._master_fd = None
        self._process = None

    def _register_reader(self) -> None:
        if self._loop is None or self._master_fd is None:
            return
        self._loop.add_reader(self._master_fd, self._on_pty_ready)
        self._reader_registered = True

    def _on_pty_ready(self) -> None:
        if self._master_fd is None:
            return
        try:
            data = os.read(self._master_fd, 4096)
        except BlockingIOError:
            return
        except OSError:
            data = b""

        if not data:
            self._closed_message = Text("(terminal session ended)", style="italic dim")
            if self._loop and self._master_fd is not None and self._reader_registered:
                self._loop.remove_reader(self._master_fd)
                self._reader_registered = False
            return

        decoded = data.decode(errors="ignore")
        try:
            self._stream.feed(decoded)
        except Exception:  # noqa: BLE001
            # If pyte raises due to malformed escape codes, ignore the frame.
            pass
        self.refresh()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def render(self) -> Text:
        if self._closed_message.plain:
            return self._closed_message.copy()

        lines: list[Text] = []
        cursor_x = getattr(self._screen.cursor, "x", 0)
        cursor_y = getattr(self._screen.cursor, "y", 0)

        for row in range(self._screen.lines):
            buffer_row = self._screen.buffer[row]
            line = Text()
            for column in range(self._screen.columns):
                cell = buffer_row[column]
                glyph = cell.data or " "
                style = self._style_for_cell(cell)
                if row == cursor_y and column == cursor_x:
                    style = style + Style(reverse=True)
                line.append(glyph, style=style)
            lines.append(line)

        return Text("\n").join(lines)

    @staticmethod
    def _style_for_cell(cell: pyte.screens.Char) -> Style:
        foreground = _resolve_color(cell.fg)
        background = _resolve_color(cell.bg)

        if cell.reverse:
            foreground, background = background, foreground

        return Style(
            color=None if foreground == "default" else foreground,
            bgcolor=None if background == "default" else background,
            bold=cell.bold or False,
            italic=cell.italics or False,
            underline=cell.underscore or False,
            strike=cell.strikethrough or False,
        )

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------
    async def on_key(self, event: events.Key) -> None:
        if not self._can_write():
            return

        data = self._serialise_key(event)
        if data is None:
            return

        event.stop()
        try:
            os.write(self._master_fd, data)
        except OSError:
            pass

    def _can_write(self) -> bool:
        return self._master_fd is not None and self._process is not None

    def _serialise_key(self, event: events.Key) -> bytes | None:
        if event.key in _SPECIAL_KEYS:
            return _SPECIAL_KEYS[event.key]

        if event.key.startswith("ctrl+") and len(event.key) == 6:
            letter = event.key[-1]
            if "a" <= letter <= "z":
                return bytes([ord(letter) - 96])

        if event.key == "enter":
            return b"\r"
        if event.key == "backspace":
            return b"\x7f"
        if event.character:
            return event.character.encode()

        return None

    # ------------------------------------------------------------------
    # Resizing
    # ------------------------------------------------------------------
    async def on_resize(self, _event: events.Resize) -> None:
        self._apply_current_size()

    def _apply_current_size(self) -> None:
        if self._master_fd is None:
            return

        width = max(int(self.size.width or _DEFAULT_COLUMNS), 2)
        height = max(int(self.size.height or _DEFAULT_ROWS), 2)

        if width != self._screen.columns or height != self._screen.lines:
            self._screen.resize(height, width)

        winsize = struct.pack("HHHH", height, width, 0, 0)
        try:
            fcntl.ioctl(self._master_fd, termios.TIOCSWINSZ, winsize)
        except OSError:
            pass


_COLOR_ALIASES = {
    "brightblack": "#808080",
    "brown": "yellow",
}


def _resolve_color(raw: Any) -> str:
    if raw is None:
        return "default"
    value = str(raw)
    if value in _COLOR_ALIASES:
        return _COLOR_ALIASES[value]
    if value.startswith("#"):
        return value
    if len(value) == 6 and all(c in "0123456789abcdefABCDEF" for c in value):
        return f"#{value}"
    return value


_SPECIAL_KEYS: dict[str, bytes] = {
    "tab": b"\t",
    "escape": b"\x1b",
    "up": b"\x1b[A",
    "down": b"\x1b[B",
    "right": b"\x1b[C",
    "left": b"\x1b[D",
    "home": b"\x1b[H",
    "end": b"\x1b[F",
    "delete": b"\x1b[3~",
    "pageup": b"\x1b[5~",
    "pagedown": b"\x1b[6~",
    "shift+tab": b"\x1b[Z",
    "f1": b"\x1bOP",
    "f2": b"\x1bOQ",
    "f3": b"\x1bOR",
    "f4": b"\x1bOS",
    "f5": b"\x1b[15~",
    "f6": b"\x1b[17~",
    "f7": b"\x1b[18~",
    "f8": b"\x1b[19~",
    "f9": b"\x1b[20~",
    "f10": b"\x1b[21~",
    "f11": b"\x1b[23~",
    "f12": b"\x1b[24~",
}
