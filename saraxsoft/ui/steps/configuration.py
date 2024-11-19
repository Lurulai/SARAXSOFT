"""Contains the ConfigurationFrame class, which is a custom tkinter frame that contains the configuration page."""

from __future__ import annotations

import customtkinter
from PIL import Image

from saraxsoft.settings import AppConfig
from saraxsoft.ui.common.label_separator import LabelSeparator
from saraxsoft.utils.enums import ConfigurationType


class ConfigurationFrame(customtkinter.CTkFrame):
    """A custom tkinter frame that contains all the navigation buttons."""

    def __init__(self, parent: customtkinter.CTk) -> None:
        """
        Initialize the ConfigurationFrame.

        Parameters
        ----------
        parent : customtkinter.CTk
            The parent of the frame.
        """
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.parent = parent
        self.config_map: dict[str, tuple[customtkinter.CTkLabel, customtkinter.CTkEntry | customtkinter.CTkComboBox | customtkinter.CTkCheckBox]] = {}

        # Load the images of configurations
        self.config_images = {
            ConfigurationType.FOUR_ARMS: customtkinter.CTkImage(
                light_image=Image.open(AppConfig._ASSET_PATH / "images" / "four-nobg.png"),
                dark_image=Image.open(AppConfig._ASSET_PATH / "images" / "four-nobg.png"),
                size=(160, 150),
            ),
            ConfigurationType.FOUR_ARMS_X: customtkinter.CTkImage(
                light_image=Image.open(AppConfig._ASSET_PATH / "images" / "four_x-nobg.png"),
                dark_image=Image.open(AppConfig._ASSET_PATH / "images" / "four_x-nobg.png"),
                size=(160, 150),
            ),
            ConfigurationType.SIX_ARMS: customtkinter.CTkImage(
                light_image=Image.open(AppConfig._ASSET_PATH / "images" / "six-nobg.png"),
                dark_image=Image.open(AppConfig._ASSET_PATH / "images" / "six-nobg.png"),
                size=(160, 150),
            ),
            ConfigurationType.EIGHT_ARMS: customtkinter.CTkImage(
                light_image=Image.open(AppConfig._ASSET_PATH / "images" / "eight-nobg.png"),
                dark_image=Image.open(AppConfig._ASSET_PATH / "images" / "eight-nobg.png"),
                size=(160, 150),
            ),
        }

        # Configure the grid layout
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create the UI
        self._create_ui()

    def _create_ui(self) -> None:
        """Create a scrollable frame for horizontal scrolling."""
        # Top level title
        self.title_area = customtkinter.CTkFrame(self, fg_color="transparent")
        self.title_area.grid(row=0, column=0, sticky="ew", pady=5)

        # Create a label separator
        self.sep = LabelSeparator(self.title_area, "Configuration")
        self.sep.grid(row=0, column=0, sticky="ew", pady=(5, 0), padx=10)

        # Create a description label
        self.description_label = customtkinter.CTkLabel(self.title_area, text="Select a configuration to continue.")
        self.description_label.grid(row=1, column=0, sticky="ew", pady=(5, 0), padx=10)

        # Create scrollable frame
        self.scrollable_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_rowconfigure(0, weight=1)

        # Add content to the scrollable frame
        self._populate_scrollable_frame()

    def _populate_scrollable_frame(self) -> None:
        """Populate the scrollable frame with horizontally arranged content."""
        # Compute button width based on the frame size and the number of items
        total_items = len(ConfigurationType)
        button_width = self.scrollable_frame.winfo_width() // total_items - 26  # Adjust padding as needed

        for index, config_type in enumerate(ConfigurationType):
            # Create a frame for each configuration
            config_frame = customtkinter.CTkFrame(self.scrollable_frame, corner_radius=10, fg_color="transparent")
            config_frame.grid(row=0, column=index, sticky="nsew", padx=13, pady=(0, 50))
            config_frame.grid_rowconfigure(0, weight=1)

            # Create a button to select the configuration
            button = customtkinter.CTkButton(
                config_frame,
                text=config_type.name.replace("_", " ").title(),
                height=200,
                width=button_width,
                image=self.config_images[config_type],
                compound="top",
                command=lambda config_type=config_type: self._select_config(config_type),
            )
            button.grid(row=0, column=0, sticky="ew", pady=(0, 10))

    def _select_config(self, config_type: ConfigurationType) -> None:
        """
        Select the configuration option.

        Parameters
        ----------
        config_type : ConfigurationType
            The configuration type of the drone.
        """
        print(f"Selected configuration: {config_type}")
