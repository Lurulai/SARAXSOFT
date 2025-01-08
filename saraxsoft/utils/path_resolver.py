"""Utility class for resolving paths relative to the project root."""

from __future__ import annotations

import sys
from pathlib import Path


class PathResolver:
    """Utility class for resolving paths relative to the project root."""

    @staticmethod
    def resolve_path(*path: str, dist_folder: bool = False) -> Path:
        """
        Resolves a path relative to the project root.

        Parameters
        ----------
        *path : str
            The path to resolve.
        dist_folder : bool, optional
            If True, the path will be resolved relative to the executable, by default False

        Returns
        -------
        Path
            The resolved path.
        """
        # If dist_folder is True, the path will be resolved relative to the executable
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            if dist_folder:
                cwd = Path.resolve(Path(sys.executable).parent)
                return cwd.joinpath(*path)
            # If the 'frozen' flag is set, we are in bundled-app mode!
            resolved_path = Path.resolve(Path(sys._MEIPASS).joinpath(*path))  # type: ignore # noqa: PGH003
        else:
            # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
            resolved_path = Path.resolve(Path.cwd().joinpath(*path))
        return resolved_path
