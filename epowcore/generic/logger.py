class Logger:
    """Global logger for the conversion changes."""

    __current_handle = -1
    __selected = -1
    __loggers: dict[int, "Logger"] = {}

    def __init__(self, handle: int, origin: str, print_to_console: bool = True) -> None:
        self.handle = handle
        """Unique identifier for the logger."""
        self.origin = origin
        """Name of the origin that is logged. Usually a converter."""
        self.print_to_console = print_to_console
        """Whether to print the log to the console."""
        self.__log_entries: list[str] = []
        """The log entries."""

    def log(self, message: str) -> None:
        """Log a message.

        :param message: The message to log.
        """
        if self.print_to_console:
            print(f"[{self.origin}] {message}")
        self.__log_entries.append(message)

    def save_to_file(self, file: str) -> None:
        """Save the log entries to a file.

        :param file: The path to the file to save the log to.
        """
        with open(file, "a", encoding="utf8") as f:
            f.write("\n".join([self.origin] + self.__log_entries))
            f.write("\n")

    def close(self) -> None:
        """Closes the current conversion changes log."""
        if self.__class__.__selected == self.handle:
            self.__class__.__selected = -1
        del Logger.__loggers[self.handle]

    @property
    def entries(self) -> list[str]:
        return self.__log_entries

    @classmethod
    def get(cls, handle: int | None = None) -> "Logger":
        """Return the logger with the given handle.

        :param handle: The handle of the logger to return. -1 to return the selected logger.
        :return: The logger with the given handle.
        """
        if handle is None:
            return cls.__loggers[cls.__selected]
        if handle not in cls.__loggers:
            raise ValueError(f"Logger with handle {handle} does not exist")
        return cls.__loggers[handle]

    @classmethod
    def select(cls, handle: int) -> None:
        """Select a logger using its handle.

        :param handle: The handle of the log to select. -1 to disable logging.
        """
        if not handle in cls.__loggers and handle != -1:
            raise ValueError(f"Logger with handle {handle} does not exist")
        cls.__selected = handle

    @classmethod
    def log_to_selected(cls, message: str) -> bool:
        """Logs a message to the currently selected logger.

        :param message: The message to log.
        :return: True if a log was selected, else False.
        """
        if cls.__selected == -1:
            return False
        cls.get(cls.__selected).log(message)
        return True

    @classmethod
    def new(cls, origin: str, select: bool = True, print_to_console: bool = True) -> "Logger":
        """Starts a new conversion changes log.

        :param origin: The name of the origin of the log messages.
        :param select: Whether to select the new log.
        :param print_to_console: Whether to print the log to the console.
        :return: The handle of the new log.
        """
        cls.__current_handle += 1
        cls.__loggers[cls.__current_handle] = Logger(
            cls.__current_handle, origin, print_to_console
        )
        if cls.__selected == -1 or select:
            cls.__selected = cls.__current_handle
        return cls.__loggers[cls.__current_handle]

    @classmethod
    def disable(cls) -> None:
        """Disable logging by unselecting the current logger."""
        cls.__selected = -1

    @classmethod
    def close_all(cls) -> None:
        """Close all previously created loggers."""
        cls.__selected = -1
        cls.__loggers = {}
