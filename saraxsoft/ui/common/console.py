"""Contains the ConsoleFrame class, which is a custom tkinter frame that contains all the console log."""

from __future__ import annotations

import datetime
import queue
import re
import tkinter as tk
from typing import TYPE_CHECKING, Any

import customtkinter

from saraxsoft.settings import ConstSettings
from saraxsoft.ui.common.popups import Popups

if TYPE_CHECKING:
    from saraxsoft.ui.state import AppState


class ConsoleFrame(customtkinter.CTkFrame):
    """A custom tkinter frame that contains all the console log."""

    ANSI_COLOR_REGEX = re.compile(r"(\x1b\[\d+(;\d+)*m)")

    def __init__(self, parent: customtkinter.CTk | customtkinter.CTkFrame, state: AppState, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the ConsoleFrame.

        Parameters
        ----------
        parent : customtkinter.CTk | customtkinter.CTkFrame
            The parent of the frame.
        state : AppState
            The shared state of the application.
        """
        super().__init__(
            parent,
            *args, **kwargs,
        )
        self.max_log_lines = 1000
        self.parent: Any = parent.parent if hasattr(parent, "parent") else parent  # type: ignore[attr-defined]
        self.app_state = state

        # Initialize a queue for message handling
        self.log_queue: queue.Queue[str] = queue.Queue()

        self.text_widget = tk.Text(self, state="disabled", wrap="word", bg="black", fg="white", highlightthickness=0)
        self.text_widget.pack(expand=True, fill="both", padx=5, pady=(5, 5), ipadx=5, ipady=5)

        self.copy_button = customtkinter.CTkButton(self.text_widget, text="📋", height=32, width=32, command=self.copy_text_to_clipboard, fg_color="#607180", hover_color="#31414F")
        self.copy_button.pack(pady=5, padx=5, anchor="e")

        # Define tags for various colors/styles
        self.text_widget.tag_config("default", foreground="white")  # Default text color
        self.text_widget.tag_config("black", foreground="black")
        self.text_widget.tag_config("red", foreground="red")
        self.text_widget.tag_config("green", foreground="green")
        self.text_widget.tag_config("yellow", foreground="yellow")
        self.text_widget.tag_config("blue", foreground="blue")
        self.text_widget.tag_config("magenta", foreground="magenta")
        self.text_widget.tag_config("cyan", foreground="cyan")
        self.text_widget.tag_config("white", foreground="white")

        # Configure the observer
        self.app_state.add_observer(self.change_appearance)

        # Update the console
        self._update_console()

    def change_appearance(self) -> None:
        """Change the appearance of the console frame based on the app state."""
        # Get the current appearance mode from the app state
        appearance_mode = self.app_state.get_appearance_mode()
        if appearance_mode == "Dark":
            self.text_widget.configure(background="#000000", fg="#FFFFFF")
            self.copy_button.configure(fg_color="#607180", hover_color="#31414F", bg_color="#000000")
        else:
            # Gray background for light mode to match the theme
            self.text_widget.configure(background="#F0F0F0", fg="#000000")
            self.copy_button.configure(fg_color="#D1D1D1", hover_color="#B0B0B0", bg_color="#F0F0F0")

        # Update the tags with the new colors
        for tag in ["default", "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]:
            self.text_widget.tag_config(tag, foreground="black" if appearance_mode == "Light" else "white")

        # Update the console with the new appearance
        self._update_console()

    def copy_text_to_clipboard(self) -> None:
        """Copy the text in the console to the clipboard."""
        self.clipboard_clear()  # Clear the clipboard
        text = self.text_widget.get("1.0", "end-1c")  # Get text from the Text widget
        self.clipboard_append(text)  # Append text to the clipboard
        Popups.one_button_popup(
            self.parent,
            (ConstSettings.MAIN_WIDTH, ConstSettings.MAIN_HEIGHT),
            (ConstSettings.EXIT_WIDTH, ConstSettings.EXIT_HEIGHT),
            "Success",
            "Text copied to clipboard.",
            "OK",
            button_command=self._close_popup,
            button_args={}
        )

    def _close_popup(self, popup: customtkinter.CTkToplevel) -> None:
        """
        Close the popup.

        Parameters
        ----------
        popup : customtkinter.CTkToplevel
            The popup to close.
        """
        if popup:
            popup.destroy()

    def _trim_log(self) -> None:
        """Trim the log to ensure it doesn't exceed the maximum number of lines."""
        try:
            current_line = int(self.text_widget.index("end-1c").split(".")[0])
        except ValueError:
            return
        if current_line > self.max_log_lines:
            line_count_to_remove = int(self.text_widget.index("end-1c").split(".")[0]) - self.max_log_lines
            self.text_widget.config(state="normal")
            self.text_widget.delete("1.0", f"{line_count_to_remove}.0")

    def write(self, msg: str, source: str = "INFO") -> None:
        """
        Write a message to the console.

        Parameters
        ----------
        msg : str
            The message to write to the console.
        source : str, optional
            The source of the message, by default "INFO"
        """
        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"{timestamp} [{source}] {msg}"
        # Remove the splitting logic and queue the entire message
        self.log_queue.put(formatted_msg)

    def _update_console(self) -> None:
        """Update the console with new messages."""
        self._trim_log()
        while not self.log_queue.empty():
            full_text = self.log_queue.get_nowait()
            self.text_widget.config(state="normal")

            # Initialize the starting index and the current color
            last_end = 0
            current_color = "default"
            # Replace it with ANSI code
            if "[STDOUT]" in full_text:
                full_text = full_text.replace("[STDOUT]", "\x1b[35m[STDOUT]\x1b[0m")
            elif "[STDERR] INFO" in full_text:
                full_text = full_text.replace("[STDERR] INFO", "\x1b[36m[STDERR] INFO\x1b[0m")
            elif "[STDERR]" in full_text:
                full_text = full_text.replace("[STDERR]", "\x1b[91m[STDERR]\x1b[0m")

            # Find all matches of the ANSI regex
            for match in ConsoleFrame.ANSI_COLOR_REGEX.finditer(full_text):
                # Get the text before the ANSI code
                text_before_ansi = full_text[last_end:match.start()]
                self.text_widget.insert(tk.END, text_before_ansi, current_color)

                # Get the ANSI sequence and change the current color
                ansi_sequence = match.group(1)
                current_color = self._ansi_to_tag(ansi_sequence) or "default"

                # Update the last_end index
                last_end = match.end()

            # Insert the remaining part of the message after the last ANSI code
            remaining_text = full_text[last_end:]
            if remaining_text:
                self.text_widget.insert(tk.END, remaining_text, current_color)

            # Ensure a newline at the end if not present
            if not full_text.endswith("\n"):
                self.text_widget.insert(tk.END, "\n", "default")

            self.text_widget.config(state="disabled")
            self.text_widget.see(tk.END)  # Auto-scroll to the bottom
        self.after(100, self._update_console)

    def _ansi_to_tag(self, ansi_sequence: str) -> str | None:
        """Convert an ANSI escape code to a Tkinter tag."""
        ansi_to_color = {
            "\x1b[0m": "default",   # Reset to default
            "\x1b[31m": "red",      # Red
            "\x1b[32m": "green",    # Green
            "\x1b[33m": "yellow",   # Yellow
            "\x1b[34m": "blue",     # Blue
            "\x1b[35m": "magenta",  # Magenta
            "\x1b[36m": "cyan",     # Cyan
            "\x1b[37m": "white",    # White
            "\x1b[93m": "yellow",   # Bright yellow
            "\x1b[92m": "green",    # Bright green
            "\x1b[91m": "red",      # Bright red
            # Add more mappings as needed
        }
        return ansi_to_color.get(ansi_sequence)
