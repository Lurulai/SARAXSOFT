"""Singleton shared state for managing the app's configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from collections.abc import Callable

    from saraxsoft.common.enums import ConfigurationType


class AppState:
    """Singleton shared state for managing the app's configuration."""

    _instance = None
    _observers: list[Callable[..., Any]]

    selected_configuration: ConfigurationType | None
    appearance_mode: str

    def __new__(cls) -> Self:
        """Create a new instance of the AppState."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._observers = []
            cls._instance.selected_configuration = None
            cls._instance.appearance_mode = "Dark"
        return cls._instance

    def set_selected_configuration(self, configuration: ConfigurationType) -> None:
        """
        Set the selected setup and notify observers.

        Parameters
        ----------
        configuration : ConfigurationType
            The selected configuration.
        """
        self.selected_configuration = configuration
        self._notify_observers()

    def set_appearance_mode(self, mode: str) -> None:
        """
        Set the appearance mode.

        Parameters
        ----------
        mode : str
            The appearance mode to set.
        """
        self.appearance_mode = mode
        self._notify_observers()

    def get_selected_configuration(self) -> ConfigurationType | None:
        """
        Get the currently selected setup.

        Returns
        -------
        ConfigurationType | None
            The currently selected setup.
        """
        return self.selected_configuration

    def get_appearance_mode(self) -> str:
        """
        Get the appearance mode.

        Returns
        -------
        str
            The appearance mode.
        """
        return self.appearance_mode

    def add_observer(self, callback: Callable[..., Any]) -> None:
        """
        Add a callback to be notified on state changes.

        Parameters
        ----------
        callback : Callable[..., Any]
            The callback to be notified.
        """
        self._observers.append(callback)

    def _notify_observers(self) -> None:
        """Notify all registered observers of state changes."""
        for callback in self._observers:
            callback()
