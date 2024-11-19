"""File containing the popup classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import customtkinter

from saraxsoft.settings import ConstSettings

if TYPE_CHECKING:
    from collections.abc import Callable


class Popups:
    """Used to create popups for the application."""

    @staticmethod
    def one_button_popup(
        parent_frame: customtkinter.CTkFrame | customtkinter.CTk,
        parent_dim: tuple[int, int],
        popup_dim: tuple[int, int],
        popup_title: str,
        popup_desc: str,
        button_text: str,
        button_command: Callable[..., Any],
        button_args: dict[str, Any],
    ) -> customtkinter.CTkToplevel:
        """
        Creates a popup with one button.

        Parameters
        ----------
        parent_frame : customtkinter.CTkFrame
            The parent frame of the popup.
        parent_dim : tuple[int, int]
            The dimensions of the parent frame.
        popup_dim : tuple[int, int]
            The dimensions of the popup.
        popup_title : str
            The title of the popup.
        popup_desc : str
            The description of the popup.
        button_text : str
            The text of the button.
        button_command : function
            The command of the button.
        button_args : tuple
            The arguments of the button command.

        Returns
        -------
        customtkinter.CTkToplevel
            The created popup.
        """
        # Create a top level dialog
        popout = customtkinter.CTkToplevel(parent_frame)
        popout.attributes("-topmost", "true")

        # Placement of the dialog
        # calculate x and y coordinates for the dialog window
        popout_x = int((parent_frame.winfo_x() + parent_dim[0] / 2) - (popup_dim[0] / 2))
        popout_y = int((parent_frame.winfo_y() + parent_dim[1] / 2) - (popup_dim[1] / 2))
        popout.geometry(f"{popup_dim[0]}x{popup_dim[1]}+{popout_x}+{popout_y}")
        # Disable resize
        popout.resizable(False, False)

        # Set the title and the information
        popout.title(popup_title)
        label = customtkinter.CTkLabel(
            master=popout,
            text=popup_desc,
            text_color=ConstSettings.DEFAULT_DESC_COLOR
        )
        label.pack(pady=(13, 30))

        button_args = button_args or {"popup": popout}
        quit_button = customtkinter.CTkButton(
            master=popout,
            text=button_text,
            command=lambda: button_command(**button_args),
            text_color=ConstSettings.ACTION_BUTTON_TEXT,
            fg_color=ConstSettings.ACTION_BUTTON_COLOR,
            hover_color=ConstSettings.ACTION_BUTTON_HOVER
        )
        quit_button.place(relx=0.5, rely=0.68, anchor=customtkinter.CENTER)

        # Grab the focus in the dialog window
        popout.grab_set()
        popout.focus_set()

        return popout

    @staticmethod
    def two_button_popup(
        parent_frame: customtkinter.CTkFrame | customtkinter.CTk,
        parent_dim: tuple[int, int],
        popup_dim: tuple[int, int],
        popup_title: str,
        popup_desc: str,
        right_button_text: str,
        left_button_text: str,
        right_button_command: Callable[..., Any],
        right_button_args: dict[str, Any],
        left_button_command: Callable[..., Any] | None = None,
        left_button_args: dict[str, Any] | None = None,
    ) -> customtkinter.CTkToplevel:
        """
        Creates a popup with two buttons.

        Parameters
        ----------
        parent_frame : customtkinter.CTkFrame
            The parent frame of the popup.
        parent_dim : tuple[int, int]
            The dimensions of the parent frame.
        popup_dim : tuple[int, int]
            The dimensions of the popup.
        popup_title : str
            The title of the popup.
        popup_desc : str
            The description of the popup.
        right_button_text : str
            The text of the first button.
        left_button_text : str
            The text of the second button.
        right_button_command : function
            The command of the second button.
        right_button_args : tuple
            The arguments of the second button command.
        left_button_command : function, optional
            The command of the first button.
        left_button_args : tuple, optional
            The arguments of the first button command.

        Returns
        -------
        customtkinter.CTkToplevel
            The created popup.
        """
        # Create a top level dialog
        popout = customtkinter.CTkToplevel(parent_frame)
        popout.attributes("-topmost", "true")

        # Placement of the dialog
        # calculate x and y coordinates for the dialog window
        popout_x = int((parent_frame.winfo_x() + parent_dim[0] / 2) - (popup_dim[0] / 2))
        popout_y = int((parent_frame.winfo_y() + parent_dim[1] / 2) - (popup_dim[1] / 2))
        popout.geometry(f"{popup_dim[0]}x{popup_dim[1]}+{popout_x}+{popout_y}")
        # Disable resize
        popout.resizable(False, False)

        # Set the title and the information
        popout.title(popup_title)
        label = customtkinter.CTkLabel(
            master=popout,
            text=popup_desc,
            text_color=ConstSettings.DEFAULT_DESC_COLOR
        )
        label.pack(pady=(13, 30))

        if left_button_command:
            left_button_args = left_button_args or {"popup": popout}
            minimize_button = customtkinter.CTkButton(
                master=popout,
                text=right_button_text,
                command=lambda: left_button_command(**left_button_args),
                text_color=ConstSettings.NORMAL_BUTTON_TEXT,
                fg_color=ConstSettings.NORMAL_BUTTON_COLOR,
                hover_color=ConstSettings.NORMAL_BUTTON_HOVER
            )
            minimize_button.place(relx=0.27, rely=0.68, anchor=customtkinter.CENTER)

        right_button_args = right_button_args or {"popup": popout}
        quit_button = customtkinter.CTkButton(
            master=popout,
            text=left_button_text,
            command=lambda: right_button_command(**right_button_args),
            text_color=ConstSettings.ACTION_BUTTON_TEXT,
            fg_color=ConstSettings.ACTION_BUTTON_COLOR,
            hover_color=ConstSettings.ACTION_BUTTON_HOVER
        )
        quit_button.place(relx=0.73, rely=0.68, anchor=customtkinter.CENTER)

        # Grab the focus in the dialog window
        popout.grab_set()
        popout.focus_set()

        return popout
