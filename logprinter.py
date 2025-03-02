################################################################
# Header

__package_name__ = "logprinter"
__version__ = "v1.0"
__license__ = "Unlicense"

__author__ = "mkow04"
__email__ = "maciejkowalski04@proton.me"

__all__ = ["LogLevel", "ThemeEntry", "Theme", "DEFAULT_THEME", "Logprinter"]


################################################################
# Imports

from pathlib import Path
from datetime import datetime, timezone
from enum import Enum
from typing import NamedTuple, TypedDict

from colorclasses import Color, Effect


################################################################
# Definitions

class LogLevel(Enum):
    DEBUG = 0
    NORMAL = 1
    PROMPT = 2
    MOTD = 3
    INFO = 4
    WARN = 5
    ERROR = 6


class ThemeEntry(NamedTuple):
    display: str
    primary: Color
    secondary: Color
    quote: Color = Color.WHITE
    time: Color = Color.DARK_GRAY


Theme = TypedDict("Theme", {level: ThemeEntry for level in LogLevel})


################################################################
# Default theme

DEFAULT_THEME: Theme = {
    LogLevel.DEBUG:  ThemeEntry(display="λ", primary=Color.DARK_MAGENTA,   secondary=Color.MAGENTA),
    LogLevel.NORMAL: ThemeEntry(display="x", primary=Color.DARK_GRAY,      secondary=Color.GRAY),
    LogLevel.PROMPT: ThemeEntry(display="%", primary=Color.DARK_GREEN,     secondary=Color.GREEN),
    LogLevel.MOTD:   ThemeEntry(display="-", primary=Color.DARK_BLUE,      secondary=Color.BLUE),
    LogLevel.INFO:   ThemeEntry(display="i", primary=Color.DARK_CYAN,      secondary=Color.CYAN),
    LogLevel.WARN:   ThemeEntry(display="!", primary=Color.DARK_YELLOW,    secondary=Color.YELLOW),
    LogLevel.ERROR:  ThemeEntry(display="‼", primary=Color.DARK_RED,       secondary=Color.RED),
}


################################################################

def get_utc_time(timezone=timezone.utc, format="%Y-%m-%dT%H:%M:%SZ") -> str:
    utc_time = datetime.now(timezone)
    return utc_time.strftime(format)


class Logprinter:
    def __init__(self,
                 is_printing_enabled: bool = True,
                 is_printing_time: bool = True,
                 print_level: LogLevel = LogLevel.NORMAL,

                 file_log_path_folder: str = None,
                 file_log_level: LogLevel = LogLevel.DEBUG,

                 is_raising_exceptions: bool = True,

                 theme: Theme = DEFAULT_THEME,
                 timezone: timezone = timezone.utc,
                 date_format: str = "%b %d %H:%M:%S"):

        self.is_printing_enabled = is_printing_enabled
        self.is_printing_time = is_printing_time
        self.print_level = print_level

        self.is_raising_exceptions = is_raising_exceptions

        self.theme = theme
        self.timezone = timezone
        self.date_format = date_format

        if file_log_path_folder is not None:
            self.file_log_level = file_log_level
            self.file_log_path_folder = Path(file_log_path_folder).expanduser()
            self.file_log_name = get_utc_time(format="%Y-%m-%dT%H:%M:%SZ.log")
            self.file_log_path = self.file_log_path_folder / self.file_log_name

            try:
                self.file_log_path_folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                if self.is_printing_enabled:
                    self.print_log(self.format_log(f"Logprinter: Error occured when initializing the log file: '{e}'", LogLevel.ERROR))
                if self.is_raising_exceptions:
                    raise e
        else:
            self.file_log_level = None
            self.file_log_path_folder = None
            self.file_log_name = None
            self.file_log_path = None

################################
# Logging to file

    def append_to_log_file(self, line_to_append):
        try:
            with open(self.file_log_path, "a", errors="ignore") as log_file:
                log_file.write(line_to_append+"\n")

        except Exception as e:
            if self.is_printing_enabled:
                self.print_log(self.format_log(f"Logprinter: Error occured when appending to log file: '{e}'", LogLevel.ERROR))

            if self.is_raising_exceptions:
                raise e

    def save_log(self, time: str, text: str, level: LogLevel = None):
        if level is None:
            name = "NONE"
        else:
            name = level.name

        self.append_to_log_file(f"{name: <6} {time} {text}")

################################
# Logging to terminal

    def color_text(self, text: str, level: LogLevel) -> str:
        colored_text: str = ""
        quote_count: int = 0

        for char in text:
            if char == "'":
                quote_count += 1
                if quote_count % 2 == 1:
                    colored_text += f"{self.theme[level].quote}'"
                else:
                    colored_text += f"'{self.theme[level].secondary}"
            else:
                colored_text += char

        return colored_text

    def print_log(self, time: str, text: str, level: LogLevel = None):
        if level is None:
            print(text)
            return None

        theme = self.theme[level]
        colored_text = self.color_text(text, level)

        if self.is_printing_time:
            time_str = f"{theme.time}({time}){Effect.RESET} "
        else:
            time_str = ""

        level_str = f"{theme.primary}[{theme.display}]{Effect.RESET}"

        print(f"{level_str} {time_str}{theme.secondary}{colored_text}{Effect.RESET}")

################################
# Main class methods

    def log_line(self, line: str, level: LogLevel = None):
        time = get_utc_time(self.timezone, self.date_format)

        compare_value = level.value if level is not None else 1

        if self.is_printing_enabled and self.print_level.value <= compare_value:
            self.print_log(time, line, level)

        if self.file_log_path_folder is not None and self.file_log_level.value <= compare_value:
            self.save_log(time, line, level)

    def bare(self, text: str = ""):
        self.log_line(text, None)

    def debug(self, text: str = ""):
        self.log_line(text, LogLevel.DEBUG)

    def normal(self, text: str = ""):
        self.log_line(text, LogLevel.NORMAL)

    def prompt(self, text: str = ""):
        self.log_line(text, LogLevel.PROMPT)

    def motd(self, text: str = ""):
        self.log_line(text, LogLevel.MOTD)

    def info(self, text: str = ""):
        self.log_line(text, LogLevel.INFO)

    def warn(self, text: str = ""):
        self.log_line(text, LogLevel.WARN)

    def error(self, text: str = ""):
        self.log_line(text, LogLevel.ERROR)


def main():
    logger = Logprinter()  # file_log_path_folder="~/.local/state/logprinter/
    logger.bare()
    logger.motd("-"*48)
    logger.motd(f"{__package_name__.capitalize()} '{__version__}'")
    logger.motd(f"Author: '{__author__} <{__email__}>'")
    logger.motd("-"*48)
    logger.bare()


if __name__ == "__main__":
    main()
