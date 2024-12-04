"""Application entry point containing the main application loop."""

from __future__ import annotations

import os
import signal
from typing import Any, cast

import customtkinter
from PIL import ImageTk

from saraxsoft.manager.serial import SerialManager
from saraxsoft.settings import AppConfig
from saraxsoft.ui.common.popups import Popups
from saraxsoft.ui.navigation import NavigationFrame
from saraxsoft.ui.state import AppState
from saraxsoft.ui.steps.configuration import ConfigurationFrame
from saraxsoft.ui.steps.connection import ConnectionFrame
from saraxsoft.ui.steps.setup import SetupFrame
from saraxsoft.utils.path_resolver import PathResolver

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    """Application class containing the main window and functions."""

    MAIN_WIDTH = 820    # Beginning window width
    MAIN_HEIGHT = 520   # Beginning window height
    EXIT_WIDTH = 320    # Exit dialog width
    EXIT_HEIGHT = 100   # Exit dialog height

    def __init__(self) -> None:
        """Initialize the application."""
        super().__init__(fg_color=("#FFFFFF", "#121212"))

        # =============== Define the main window and appearance ===============
        customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

        # Set icon path and icon for the application
        logo_image = PathResolver.resolve_path("assets", "favicon.ico")
        self.iconpath = ImageTk.PhotoImage(file=logo_image)
        self.wm_iconbitmap()
        self.iconphoto(True, self.iconpath)  # type: ignore[reportArgumentType]

        # App state
        self.app_state = AppState()

        # Create serial manager
        self._serial_manager = SerialManager(port=AppConfig._ARDUINO_PORT)
        self._serial_manager.start()

        # Specify the delete window protocol with custom function/dialog
        self.protocol(
            name="WM_DELETE_WINDOW",
            func=lambda: Popups.one_button_popup(
                self,
                (App.MAIN_WIDTH, App.MAIN_HEIGHT),
                (App.EXIT_WIDTH, App.EXIT_HEIGHT),
                "Confirm Exit",
                "Are you sure you want to exit?",
                "Exit",
                button_command=self._quit_app,
                button_args={}
            )
        )

        # Title of the app
        self.title("SARAX")

        # Placement of the window
        center = self._center(App.MAIN_WIDTH, App.MAIN_HEIGHT)
        self.geometry(f"{self.MAIN_WIDTH}x{self.MAIN_HEIGHT}+{int(center[0])}+{int(center[1])}")
        self.resizable(False, False)

        # Configure the grid layout
        self.columnconfigure(0, weight=1)  # Make the column expandable
        self.grid_rowconfigure(0, weight=0)  # Make the top row non-expandable
        self.grid_rowconfigure(1, weight=1)  # Make the middle row expandable
        self.grid_rowconfigure(2, weight=0)  # Make the bottom row non-expandable

        # Initialize navigation frame
        self.navigation_frame = NavigationFrame(self)

        self._init_frames()  # Initialize the frames of the application

    def get_width(self) -> int:
        """Return the width of the main window."""
        return self.MAIN_WIDTH

    def get_height(self) -> int:
        """Return the height of the main window."""
        return self.MAIN_HEIGHT

    def get_center(self) -> tuple[float, float]:
        """Return the coordinates to center the window."""
        return self._center(self.MAIN_WIDTH, self.MAIN_HEIGHT)

    def get_serial_manager(self) -> SerialManager:
        """Return the serial manager."""
        return self._serial_manager

    def _center(self, window_width: int, window_height: int) -> tuple[float, float]:
        """Return the coordinates to center the window."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        return (x, y)

    def _init_frames(self) -> None:
        """Initialize the frames of the application."""
        # Create all the frames
        _connection_frame = ConnectionFrame(self, self.app_state)
        _setup_frame = SetupFrame(self, self.app_state)
        _config_frame = ConfigurationFrame(self, self.app_state)

        # Add the frames to the navigation frame
        self.navigation_frame.add_frame("Connection", 0, _connection_frame)
        self.navigation_frame.add_frame("Setup", 1, _setup_frame)
        self.navigation_frame.add_frame("Configuration", 2, _config_frame)

        # Select the home frame
        self.navigation_frame.select_frame_by_name("Connection")

    def _quit_app(self, **kwargs: dict[str, Any]) -> None:
        """
        Function to destroy the window.

        Parameters
        ----------
        popup: customtkinter.CTkToplevel
            The popup to destroy.
        """
        if "popup" in kwargs:
            popup: customtkinter.CTkToplevel = cast(customtkinter.CTkToplevel, kwargs["popup"])
            popup.grab_release()
            popup.destroy()
        # Stop the serial manager
        self._serial_manager.stop()
        # Destroy the main window
        self.destroy()
        os.kill(os.getpid(), signal.SIGTERM)
