"""Enums for the application."""

from __future__ import annotations

from enum import StrEnum


class ConfigurationType(StrEnum):
    """Drone configuration type."""

    FOUR_ARMS = "4-Arms"
    FOUR_ARMS_X = "4-Arms-X"
    SIX_ARMS = "6-Arms"
    EIGHT_ARMS = "8-Arms"
