"""Main entrypoint."""

from __future__ import annotations

from saraxsoft.ui.app import App


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
