"""First page in the application, which is also the start page."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import TYPE_CHECKING

from saraxsoft.utils.enums import ConfigurationType
from saraxsoft.utils.image_utils import load_image
from saraxsoft.utils.path_resolver import PathResolver

if TYPE_CHECKING:
    from saraxsoft.ui.main_window import MainWindow


class FirstPage(tk.Frame):
    """First page of the application."""

    def __init__(self, parent: tk.Frame, controller: MainWindow) -> None:
        """
        Initialize the FirstPage.

        Parameters
        ----------
        parent : tk.Frame
            The parent frame.
        controller : MainWindow
            The window/frame controller.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Create a container for the three boxes
        container = ttk.Frame(self)
        container.pack(pady=20)

        # Create three frames for the boxes, passing different image paths
        self.create_box(container, "Four-Plus", PathResolver.resolve_path("assets/images/four.png"), ConfigurationType.FOUR_ARMS)
        self.create_box(container, "Four-X", PathResolver.resolve_path("assets/images/four_x.png"), ConfigurationType.FOUR_ARMS_X)
        self.create_box(container, "Six", PathResolver.resolve_path("assets/images/six.png"), ConfigurationType.SIX_ARMS)
        self.create_box(container, "Eight", PathResolver.resolve_path("assets/images/eight.png"), ConfigurationType.EIGHT_ARMS)

    def create_box(self, container: ttk.Frame, label_text: str, image_path: Path, config_type: ConfigurationType) -> None:
        """
        Create a box with the correct configuration.

        Parameters
        ----------
        container : ttk.Frame
            The container frame containing the config type.
        label_text : str
            The label text.
        image_path : Path
            The location of the image.
        config_type : ConfigurationType
            The drone configuration type.
        """
        frame = ttk.Frame(container, relief="solid", borderwidth=60)
        frame.pack(side="left", padx=21, pady=53)

        # Load the image
        image_tk = load_image(image_path, (100, 100))

        if image_tk:
            image_label = ttk.Label(frame, image=image_tk)  # type: ignore[type-correct]
            image_label.image = image_tk  # type: ignore[type-correct]
        else:
            image_label = ttk.Label(frame, text="[Image Not Found]")

        image_label.pack(pady=10)

        button = ttk.Button(
            frame,
            text=f"Select {label_text}",
            command=lambda: self.select_config(config_type),
        )
        button.pack(pady=10)

    def select_config(self, config_type: ConfigurationType) -> None:
        """
        Select the configuration option.

        Parameters
        ----------
        config_type : ConfigurationType
            The configuration type of the drone.
        label : str
            The label.
        """
        self.controller.set_config(config_type)
        self.controller.show_frame("SecondPage")
