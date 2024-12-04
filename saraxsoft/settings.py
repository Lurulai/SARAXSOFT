"""Contains all the settings for the program."""


from saraxsoft.utils.path_resolver import PathResolver


class ConstSettings:
    """Constant settings."""

    DEFAULT_TEXT_COLOR = ("#000000", "#FFFFFF")  # (Light=Black, Dark=White)

    DEFAULT_DESC_COLOR = ("#000000", "#FFFFFF")  # (Light=Black, Dark=White)
    WARNING_DESC_COLOR = ("#000000", "#FFFFFF")  # (Light=Black, Dark=White)

    NORMAL_BUTTON_TEXT = ("#000000", "#FFFFFF")  # (Light=Black, Dark=White)
    NORMAL_BUTTON_COLOR = ("#64B5F6", "#1565C0")  # (Light=Blue300, Dark=Blue800)
    NORMAL_BUTTON_HOVER = ("#42A5F5", "#0D47A1")  # (Light=Blue400, Dark=Blue900)

    ACTION_BUTTON_TEXT = ("#000000", "#FFFFFF")  # (Light=Black, Dark=White)
    ACTION_BUTTON_COLOR = ("#E57373", "#C62828")  # (Light=Red300, Dark=Red800)
    ACTION_BUTTON_HOVER = ("#EF5350", "#B71C1C")  # (Light=Red400, Dark=Red900)

    DEFAULT_ENTRY_BORDER_COLOR = ("#9D9D9D", "#595959")  # (Light=Grey600, Dark=Grey800)
    CHANGED_ENTRY_BORDER_COLOR = ("#64B5F6", "#1565C0")  # (Light=Blue300, Dark=Blue800)
    INVALID_ENTRY_BORDER_COLOR = ("#E57373", "#C62828")  # (Light=Red300, Dark=Red800)


class AppConfig:
    """Configuration for the app."""

    _ASSET_PATH = PathResolver.resolve_path("assets")
    _ARDUINO_PORT = "/dev/cu.usbserial-120"
