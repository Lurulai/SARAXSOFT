"""Main entrypoint."""

from __future__ import annotations

import tkinter as tk

from saraxsoft.ui.main_window import MainWindow

# Constants for Arduino connection
arduino_port: str = "COM3"  # The port where the Arduino is connected
baud_rate: int = 9600       # Baud rate for serial communication


def main():
    """
    Initialize and run the application.

    This function creates the root Tkinter window, initializes the MainWindow
    application, and starts the Tkinter event loop.
    """
    root = tk.Tk()
    _app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
