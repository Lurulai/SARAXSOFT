"""Contains the ConfigurationFrame class, which is a custom tkinter frame that contains the configuration page."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

import customtkinter

from saraxsoft.common.enums import ConfigurationType
from saraxsoft.settings import ConstSettings
from saraxsoft.ui.common.console import ConsoleFrame
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
        self.circles: list[tuple[int, int, str, str]] = []
        self.circle_ids: list[int] = []
        self.current_circle_index = 0
        self.pin_mapping = {}
        self.expected_values = {}

        # Keep track of the tasks
        self.blinking_task = None
        self.auto_step_task = None

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Configure the observer
        self.app_state.add_observer(self._update_config)
        self.app_state.add_observer(self._change_appearance)

        # Register the connection observer
        self.parent.get_comm_manager().add_connection_observer(self._on_connection_change)

        # Get the comm manager
        self.comm_manager = self.parent.get_comm_manager()
        self.comm_manager.add_command_handler(self._log_to_console)

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

        self.data_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.data_frame.grid_columnconfigure(1, weight=1, uniform="group1")
        self.data_frame.grid_rowconfigure(0, weight=1)

        # Canvas for drawing arms
        self.canvas = tk.Canvas(self.data_frame, highlightthickness=0, background="#131212", width=ConstSettings.MAIN_WIDTH // 2)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=10)

        # Log text widget
        self.console_frame = ConsoleFrame(self.data_frame, self.app_state, width=ConstSettings.MAIN_WIDTH // 2, fg_color="transparent")
        self.console_frame.grid(row=0, column=1, sticky="nsew", padx=10)

    def _log_to_console(self, message: str) -> None:
        """Update the Text widget with a new log message."""
        # Skip empty and pong messages
        if not message or message.lower() == "pong":
            return
        self.console_frame.write(message)

    def _update_config(self) -> None:
        """Update the configuration drawing based on the selected setup."""
        # Cancel any existing blinking task
        if self.blinking_task is not None:
            self.after_cancel(self.blinking_task)
            self.blinking_task = None
        if self.auto_step_task is not None:
            self.after_cancel(self.auto_step_task)
            self.auto_step_task = None

        # Clear existing canvas
        self.canvas.delete("all")
        self.circle_ids.clear()

        # Get the selected configuration from the app state
        selected_config = self.app_state.get_selected_configuration()
        if not selected_config:
            return
        self.description_label.configure(text=f"Selected Configuration: {selected_config.name.replace('_', ' ').title()}")

        # Map configurations to arm positions
        self.circles = self._get_circle_positions(selected_config)
        if not self.circles:
            self.canvas.create_text(
                200, 200, text="Invalid Configuration", fill="red", font=("Arial", 16)
            )
            return

        # Draw circles on the canvas
        self._draw_circles()

        # Create pin mapping
        self.pin_mapping = {i: i for i in range(len(self.circles))}
        self.expected_device_values: list[int] = [1, 0] * (len(self.circles) // 2)
        self.comm_manager.set_connected_device_lines(len(self.circles))

        # Start auto-stepping through the circles
        if self.circle_ids:
            self.current_circle_index = 0
            self._start_blink()
            self._auto_step()

    def _change_appearance(self) -> None:
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

    def _draw_circles(self) -> None:
        """Draw circles on the canvas based on the configuration."""
        for x, y, color, label in self.circles:
            circle_id = self.canvas.create_oval(
                x - 20, y - 20, x + 20, y + 20, fill=color, outline="black"
            )
            self.canvas.create_text(x, y, text=label, font=("Arial", 12), fill="black")
            self.circle_ids.append(circle_id)

    def _start_blink(self) -> None:
        """Start blinking the circle at current_circle_index."""
        if self.blinking_task is None:
            self._blink_tick()

    def _blink_tick(self) -> None:
        if not self.circle_ids:
            return

        # Toggle color between red and original
        circle_id = self.circle_ids[self.current_circle_index]
        current_color = self.canvas.itemcget(circle_id, "fill")
        original_color = self._get_original_color()

        if current_color != "red":
            self.canvas.itemconfig(circle_id, fill="red")
        else:
            self.canvas.itemconfig(circle_id, fill=original_color)

        self.blinking_task = self.after(500, self._blink_tick)

    def _stop_blink(self, index: int) -> None:
        """Stop blinking a specific circle; revert to original color."""
        if index < len(self.circle_ids):
            circle_id = self.circle_ids[index]
            orig_color = self._get_original_color()
            self.canvas.itemconfig(circle_id, fill=orig_color)

    def _on_connection_change(self, connected: bool) -> None:
        """Update the UI based on the connection status."""
        self.after(10, self._change_page, connected)

    def _change_page(self, connected: bool) -> None:
        """Change the page based on the connection status."""
        if not connected:
            self.parent.navigation_frame.select_frame_by_name("Connection")

    def _get_original_color(self) -> str:
        """Get the original color of the current circle."""
        return self.circles[self.current_circle_index][2]

    def _auto_step(self) -> None:
        """Auto-step through the circles."""
        if not self.circle_ids:
            return

        # 1. Check hardware
        pin = self.pin_mapping[self.current_circle_index]
        is_present = self.comm_manager.probe_single_pin(pin, self.expected_device_values[self.current_circle_index])

        # 2. Update color
        current_circle_id = self.circle_ids[self.current_circle_index]
        new_color = "green" if is_present else "red"
        self.canvas.itemconfig(current_circle_id, fill=new_color)

        # 3. Decide next step
        if is_present:
            # If present, move forward to the next circle
            old_index = self.current_circle_index
            self.current_circle_index = (self.current_circle_index + 1) % len(self.circle_ids)

            # Stop blinking the old circle, start blinking the new one
            self._stop_blink(old_index)
            self._start_blink()
        else:
            # If missing, backtrack
            self.current_circle_index = (self.current_circle_index - 1) % len(self.circle_ids)

            # Stop blinking the current circle
            self._stop_blink(self.current_circle_index)
            self._start_blink()

        # 4. Schedule next check
        self.auto_step_task = self.after(1000, self._auto_step)
