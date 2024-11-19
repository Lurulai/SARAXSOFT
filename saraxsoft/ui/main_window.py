"""Main window for the application UI."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from saraxsoft.ui.steps.first_page import FirstPage
from saraxsoft.ui.steps.second_page import SecondPage

if TYPE_CHECKING:
    from saraxsoft.utils.enums import ConfigurationType


class MainWindow:
    """Main window that serves as the central UI controller, managing navigation between multiple pages."""

    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the MainWindow.

        Parameters
        ----------
        root : tk.Tk
            The root Tkinter window to host the application UI.
        """
        self.root: tk.Tk = root
        self.root.title("Raspberry Pi UI")
        self.root.geometry("800x480")

        # Create a container frame to hold different pages
        self.container: tk.Frame = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # Dictionary to store frames (pages) by their class name
        self.frames: dict[str, tk.Frame] = {}

        # Holds the selected configuration, updated by pages
        self.selected_config: ConfigurationType | None = None

        # Initialize all pages and store them in the frames dictionary
        for page in (FirstPage, SecondPage):
            page_name: str = page.__name__
            frame: tk.Frame = page(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")  # Stack frames on top of each other

        # Display the first page by default
        self.show_frame("FirstPage")

    def show_frame(self, page_name: str) -> None:
        """
        Display a specific frame (page) based on the page name.

        Parameters
        ----------
        page_name : str
            The name of the page class to display (e.g., 'FirstPage', 'SecondPage').
        """
        frame: tk.Frame = self.frames[page_name]

        # Bring the frame to the front
        frame.tkraise()

    def set_config(self, config: ConfigurationType) -> None:
        """
        Set the selected configuration.

        Parameters
        ----------
        config : ConfigurationType
            The configuration string selected by the user.
        """
        self.selected_config = config
