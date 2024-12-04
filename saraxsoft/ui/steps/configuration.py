"""Contains the ConfigurationFrame class, which is a custom tkinter frame that contains the configuration page."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

import customtkinter

from saraxsoft.common.enums import ConfigurationType
from saraxsoft.ui.common.label_separator import LabelSeparator

if TYPE_CHECKING:
    from saraxsoft.ui.app import App
    from saraxsoft.ui.state import AppState


class ConfigurationFrame(customtkinter.CTkFrame):
    """A custom tkinter frame that contains the configuration page."""

    def __init__(self, parent: App, state: AppState) -> None:
        """
        Initialize the ConfigurationFrame.

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

        # Keep track of circles and their IDs
        self.circles = []
        self.circle_ids: list[int] = []
        self.current_circle_index = 0
        self.blinking_task = None

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Configure the observer
        self.app_state.add_observer(self.update_config)
        self.app_state.add_observer(self.change_appearance)

        # Create the UI
        self._create_ui()

    def _create_ui(self) -> None:
        """Initialize the UI components."""
        # Top level title
        self.title_area = customtkinter.CTkFrame(self, fg_color="transparent")
        self.title_area.grid(row=0, column=0, sticky="ew", pady=5)

        # Create a label separator
        self.sep = LabelSeparator(self.title_area, "Drone Arm Configuration")
        self.sep.grid(row=0, column=0, sticky="ew", pady=(5, 0), padx=10)

        # Create a description label
        self.description_label = customtkinter.CTkLabel(self.title_area, text="Selected Configuration: -")
        self.description_label.grid(row=1, column=0, sticky="ew", pady=(5, 0), padx=10)

        # Data frame for configuration selection
        self.data_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.data_frame.grid(row=1, column=0, sticky="nsew", pady=10)

        self.data_frame.grid_columnconfigure(0, weight=1)
        self.data_frame.grid_columnconfigure(1, weight=1)
        self.data_frame.grid_rowconfigure(0, weight=1)

        # Canvas for drawing arms
        self.canvas = tk.Canvas(self.data_frame, highlightthickness=0, background="#131212")
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=10)

        # Additional data
        self.additional_data_frame = customtkinter.CTkFrame(self.data_frame, corner_radius=0, fg_color="transparent")
        self.additional_data_frame.grid(row=0, column=1, sticky="nsew", padx=10)

    def update_config(self) -> None:
        """Update the configuration drawing based on the selected setup."""
        # Cancel any existing blinking task
        if self.blinking_task is not None:
            self.after_cancel(self.blinking_task)
            self.blinking_task = None

        # Clear existing canvas
        self.canvas.delete("all")
        self.circle_ids.clear()

        # Get the selected configuration from the app state
        selected_config = self.app_state.get_selected_configuration()
        if not selected_config:
            return
        self.description_label.configure(text=f"Selected Configuration: {selected_config.name.replace('_', '-')}")

        # Map configurations to arm positions
        self.circles = self._get_circle_positions(selected_config)
        if not self.circles:
            self.canvas.create_text(
                200, 200, text="Invalid Configuration", fill="red", font=("Arial", 16)
            )
            return

        # Draw circles on the canvas
        self._draw_circles()

    def change_appearance(self) -> None:
        """Change the appearance of the configuration frame based on the app state."""
        # Get the current appearance mode from the app state
        appearance_mode = self.app_state.get_appearance_mode()
        if appearance_mode == "Dark":
            self.canvas.configure(background="#131212")
        else:
            self.canvas.configure(background="#FFFFFF")

    def _get_circle_positions(self, config_type: ConfigurationType) -> list[tuple[int, int, str, str]]:
        """Get the circle positions for the selected configuration."""
        if config_type == ConfigurationType.FOUR_ARMS_X:
            return [
                (120, 120, "lightblue", "1"),  # Top-left
                (280, 120, "lightgreen", "2"),  # Top-right
                (280, 280, "lightcoral", "3"),  # Bottom-right
                (120, 280, "lightyellow", "4"),  # Bottom-left
            ]
        if config_type == ConfigurationType.FOUR_ARMS:
            return [
                (200, 100, "lightblue", "1"),  # Top
                (300, 200, "lightgreen", "2"),  # Right
                (200, 300, "lightcoral", "3"),  # Bottom
                (100, 200, "lightyellow", "4"),  # Left
            ]
        if config_type == ConfigurationType.SIX_ARMS:
            return [
                (200, 80, "lightblue", "1"),  # Top
                (280, 140, "lightgreen", "2"),  # Top-right
                (280, 260, "lightcoral", "3"),  # Bottom-right
                (200, 320, "lightyellow", "4"),  # Bottom
                (120, 260, "lightpink", "5"),  # Bottom-left
                (120, 140, "lightcyan", "6"),  # Top-left
            ]
        if config_type == ConfigurationType.EIGHT_ARMS:
            return [
                (200, 80, "lightblue", "1"),  # Top
                (270, 120, "lightgreen", "2"),  # Top-right
                (300, 200, "lightcoral", "3"),  # Right
                (270, 280, "lightyellow", "4"),  # Bottom-right
                (200, 320, "lightpink", "5"),  # Bottom
                (130, 280, "lightcyan", "6"),  # Bottom-left
                (100, 200, "lightgray", "7"),  # Left
                (130, 120, "lightgoldenrod", "8"),  # Top-left
            ]
        return []

    def _draw_circles(self) -> None:
        """Draw circles on the canvas based on the configuration."""
        for x, y, color, label in self.circles:
            circle_id = self.canvas.create_oval(
                x - 20, y - 20, x + 20, y + 20, fill=color, outline="black"
            )
            self.canvas.create_text(x, y, text=label, font=("Arial", 12), fill="black")
            self.circle_ids.append(circle_id)

        # Start blinking the first circle
        if self.circle_ids:
            self.current_circle_index = 0
            self.blink()

    def blink(self) -> None:
        """Blink the current circle to guide the user."""
        if not self.circle_ids:
            return

        current_circle = self.circle_ids[self.current_circle_index]
        current_color = self.canvas.itemcget(current_circle, "fill")
        original_color = self._get_original_color()

        # Toggle between red and the original color
        new_color = "red" if current_color != "red" else original_color
        self.canvas.itemconfig(current_circle, fill=new_color)

        # Schedule the next blink
        self.blinking_task = self.after(500, self.blink)

    def next_circle(self) -> None:
        """Move to the next circle and stop blinking the current one."""
        if self.blinking_task is not None:
            self.after_cancel(self.blinking_task)
            self.blinking_task = None

        # Reset the current circle's color
        current_circle = self.circle_ids[self.current_circle_index]
        self.canvas.itemconfig(current_circle, fill=self._get_original_color())

        # Move to the next circle
        self.current_circle_index = (self.current_circle_index + 1) % len(self.circle_ids)

        # Start blinking the new circle
        self.blink()

    def _get_original_color(self) -> str:
        """Get the original color of the current circle."""
        return self.circles[self.current_circle_index][2]
