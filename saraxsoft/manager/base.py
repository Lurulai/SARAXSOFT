"""Base module for the manager package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable


class ICommManager(Protocol):
    """Interface for the communication manager."""

    def add_connection_observer(self, callback: Callable[[bool], None]) -> None:
        """
        Add an observer for connection changes.

        Parameters
        ----------
        callback : Callable[[bool], None]
            The callback function to be called when the connection state changes.
        """

    def add_command_handler(self, handler: Callable[[str], None]) -> None:
        """
        Add a handler for received commands.

        Parameters
        ----------
        handler : Callable[[str], None]
            The handler function to be called when a command is received.
        """
