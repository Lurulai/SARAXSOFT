"""Main entrypoint."""

from __future__ import annotations

from saraxsoft.ui.app import App

# Constants for Arduino connection
arduino_port: str = "COM8"  # The port where the Arduino is connected
baud_rate: int = 9600       # Baud rate for serial communication

def main():
    """
    Initialize and run the application.

    This function creates the root Tkinter window, initializes the
    application, and starts the Tkinter event loop.
    """
    sarax_app = App()
    sarax_app.mainloop()


if __name__ == "__main__":
    main()
