"""Contains the NavigationFrame class, which is a custom tkinter frame that contains all the navigation buttons."""

from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter
from PIL import Image

from saraxsoft.settings import AppConfig

if TYPE_CHECKING:
    from saraxsoft.ui.app import App


class NavigationFrame(customtkinter.CTkFrame):
    """A custom tkinter frame that contains all the navigation buttons."""

    def __init__(self, parent: App) -> None:
        """
        Initialize the NavigationFrame.

        Parameters
        ----------
        parent : App
            The parent of the frame.
        """
        super().__init__(parent, corner_radius=0, fg_color="transparent", width=150, height=600)

        self.parent = parent

        self.current_frame_index = 0
        self.frame_mapping: dict[str, customtkinter.CTkFrame] = {}
        self.frame_mapping_by_index: dict[int, str] = {}

        # Configure grid layout
        self.grid(row=0, sticky="ew")  # Place navigation frame at the bottom
        self.grid_columnconfigure(0, weight=0)  # Back button (left)
        self.grid_columnconfigure(1, weight=1)  # Spacer
        self.grid_columnconfigure(2, weight=0)  # Appearance menu (right)

        # Load images for light and dark modes
        back_light_image_path = AppConfig._ASSET_PATH / "icons" / "back_light.png"
        back_dark_image_path = AppConfig._ASSET_PATH / "icons" / "back_dark.png"
        self.back_image = customtkinter.CTkImage(
            light_image=Image.open(back_light_image_path),
            dark_image=Image.open(back_dark_image_path),
            size=(20, 20),
        )

        # Create Back button
        self.back_button = customtkinter.CTkButton(
            self,
            text="",
            image=self.back_image,
            compound="left",
            corner_radius=10,
            fg_color=("#64B5F6", "#1565C0"),
            hover_color=("#42A5F5", "#0D47A1"),
            text_color=("#000000", "#FFFFFF"),
            command=self._back_command,
        )

        # button to change the theme mode of the app
        self.appearance_menu = customtkinter.CTkOptionMenu(
            master=self,
            text_color=("#000000", "#FFFFFF"),              # (Light=Black, Dark=White)
            button_color=("#64B5F6", "#1565C0"),            # (Light=Blue300, Dark=Blue800)
            button_hover_color=("#42A5F5", "#0D47A1"),      # (Light=Blue400, Dark=Blue900)
            fg_color=("#64B5F6", "#1565C0"),                # (Light=Blue300, Dark=Blue800)
            values=["Dark", "Light"],
            dropdown_fg_color=("#FFFBFE", "#1e1e1e"),       # (Light=White, Dark=Black)
            dropdown_hover_color=("#64B5F6", "#1565C0"),    # (Light=Blue300, Dark=Blue800)
            dropdown_text_color=("#000000", "#FFFFFF"),     # (Light=Black, Dark=White)
            command=self._change_appearance_mode,
        )
        self.appearance_menu.grid(row=0, column=2, padx=20, pady=(20, 0), sticky="e")

    def select_frame_by_name(self, name: str) -> None:
        """
        Selects a frame by name.

        Parameters
        ----------
        name : str
            The name of the frame to select.
        """
        # show selected frame and hide others
        for frame_name, frame in self.frame_mapping.items():
            if frame_name == name:
                frame.grid(row=1, column=0, sticky="nsew")
                frame.update_idletasks()  # Update the frame to get the correct size
            else:
                frame.grid_remove()  # Effectively hides the frame, but remembers its place

        self.current_frame_index = list(self.frame_mapping_by_index.keys())[list(self.frame_mapping_by_index.values()).index(name)]

        if self.current_frame_index == 0:
            self.back_button.grid_remove()
        else:
            self.back_button.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
            self.update_idletasks()  # Update the frame to get the correct size

    def add_frame(self, name: str, order: int, frame: customtkinter.CTkFrame) -> None:
        """
        Adds a frame to the navigation frame.

        Parameters
        ----------
        name : str
            The name of the frame
        order : int
            The order of the frame
        frame : customtkinter.CTkFrame
            The frame to add to the navigation frame
        """
        self.frame_mapping[name] = frame
        self.frame_mapping_by_index[order] = name
        frame.grid(row=1, column=0, sticky="nsew")
        frame.grid_remove()

    def _back_command(self) -> None:
        """The command to execute when the back button is clicked."""
        if self.current_frame_index > 0:
            self.select_frame_by_name(self.frame_mapping_by_index[self.current_frame_index - 1])

    def _change_appearance_mode(self, new_appearance_mode: str) -> None:
        """Change the appearance mode of the app."""
        customtkinter.set_appearance_mode(new_appearance_mode)
        self.parent.app_state.set_appearance_mode(new_appearance_mode)
