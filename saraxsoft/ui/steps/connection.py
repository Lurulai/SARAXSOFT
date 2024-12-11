"""Contains the ConnectionFrame class, which is a custom tkinter frame that contains the connection page."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import customtkinter
from PIL import Image

if TYPE_CHECKING:
    from saraxsoft.ui.app import App
    from saraxsoft.ui.state import AppState


class ConnectionFrame(customtkinter.CTkFrame):
    """A custom tkinter frame that contains the connection page."""

    def __init__(self, parent: App, state: AppState) -> None:
        """
        Initialize the ConnectionFrame.

        Parameters
        ----------
        parent : App
            The parent of the frame.
        state : AppState
            The shared state of the application.
        """
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.parent: App = parent
        self.app_state: AppState = state

        # Register the connection observer
        self.parent.get_serial_manager().add_connection_observer(self._on_connection_change)

        # Load images
        self.disconnected_image = customtkinter.CTkImage(
            light_image=Image.open(Path("assets") / "icons" / "disconnected.png"),
            dark_image=Image.open(Path("assets") / "icons" / "disconnected.png"),
            size=(160, 150),
        )
        self.connected_image = customtkinter.CTkImage(
            light_image=Image.open(Path("assets") / "icons" / "connected.png"),
            dark_image=Image.open(Path("assets") / "icons" / "connected.png"),
            size=(160, 150),
        )

        # UI Initialization
        self._create_ui()

    def _create_ui(self) -> None:
        """Initialize the UI components."""
        # Status label
        self.status_label = customtkinter.CTkLabel(
            self, text="Please connect the device. Checking device connection...", font=("Arial", 18), text_color=("#000000", "#FFFFFF")
        )
        self.status_label.grid(row=0, column=0, pady=(40, 20), padx=20)

        # Image display
        self.image_label = customtkinter.CTkLabel(self, image=self.disconnected_image, text="")
        self.image_label.grid(row=1, column=0, pady=20)

        # Continue button (initially hidden)
        self.continue_button = customtkinter.CTkButton(
            self, text="Continue", command=self._on_continue, state="disabled"
        )
        self.continue_button.grid(row=2, column=0, pady=(40, 40))

        # Center align all widgets
        self.grid_columnconfigure(0, weight=1)

    def _on_connection_change(self, connected: bool) -> None:
        """Update the UI based on the connection status."""
        self.after(10, self._update_connection_status, connected)

    def _update_connection_status(self, connected: bool) -> None:
        """Actual method to update the UI components."""
        if connected:
            self.status_label.configure(text="Device connected!", text_color="#76b977")
            self.image_label.configure(image=self.connected_image)
            self.continue_button.configure(state="normal")  # Enable button
        else:
            self.status_label.configure(text="Please connect the device. Checking device connection...", text_color=("#000000", "#FFFFFF"))
            self.image_label.configure(image=self.disconnected_image)
            self.continue_button.configure(state="disabled")  # Disable button

    def _on_continue(self) -> None:
        """Handle the continue button click event."""
        self.parent.navigation_frame.select_frame_by_name("Setup")
