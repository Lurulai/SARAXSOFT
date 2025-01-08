"""LabelSeparator Component."""

from __future__ import annotations

from typing import Any

import customtkinter


class LabelSeparator(customtkinter.CTkFrame):
    """A frame with a label in the center and separator lines on both sides."""

    def __init__(self, parent: customtkinter.CTkFrame | customtkinter.CTkScrollableFrame, label_text: str, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the LabelSeparator.

        Parameters
        ----------
        parent : customtkinter.CTkFrame | customtkinter.CTkScrollableFrame
            The parent frame to place the LabelSeparator.
        label_text : str
            The text to display in the label.
        """
        super().__init__(parent, *args, **kwargs, fg_color="transparent")

        # Configure the entire frame to expand horizontally
        self.grid(sticky="ew")
        self.grid_columnconfigure(0, weight=1)  # Make the left separator expand
        self.grid_columnconfigure(1, minsize=0)  # Middle column for label, set minsize if needed
        self.grid_columnconfigure(2, weight=1)  # Make the right separator expand

        # Create a separator line before the label
        self.separator_left = customtkinter.CTkFrame(self, height=2, fg_color="gray75")
        self.separator_left.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Create a label widget in the center
        self.label = customtkinter.CTkLabel(self, text=label_text, font=customtkinter.CTkFont(size=14, weight="bold"))
        self.label.grid(row=0, column=1)

        # Create a separator line after the label
        self.separator_right = customtkinter.CTkFrame(self, height=2, fg_color="gray75")
        self.separator_right.grid(row=0, column=2, sticky="ew", padx=(5, 0))

        # Ensure the label separator frame fills its cell in parent grid
        self.grid(sticky="ew")
        parent.grid_columnconfigure(0, weight=1)  # Make sure parent's column is set to expand
