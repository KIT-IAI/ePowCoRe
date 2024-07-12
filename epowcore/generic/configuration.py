import logging
import re
from typing import Any
import yaml

from epowcore.generic.constants import Platform
from epowcore.generic.singleton import Singleton

_REGEX_FILE_TAG = re.compile(r"<file:(.*)>")


class Configuration(metaclass=Singleton):
    """A singleton class that holds the configuration of the application, parsed from a yaml file."""

    def __init__(self) -> None:
        self.default_platform: Platform | None = None
        """The currently selected platform to get default values for."""
        self.__configs: list[tuple[int, dict]] = []
        """A list of configuration dictionaries and their priorities, always sorted by descending priority."""

        self.load_config("config.yml")

    def get(self, key: str) -> Any:
        """Static access method.

        :param key: The key of the configuration value.
        """
        for _, conf in self.__configs:
            value = self.__get_from_config(key, conf)
            if value is not None:
                return value
        return None

    def get_default(
        self, component: str, attr: str, platform: Platform | None = None
    ) -> Any | None:
        """Get the default value for a component attribute for the specified platform.
        If no platform is specified, uses the [default_platform] the Configuration is set to.
        Uses global default values as a fallback.

        :param component: The component type to get the value for.
        :type component: str
        :param attr: The attribute name.
        :type attr: str
        :param platform: The platform to get the value for; defaults to None.
        :type platform: Platform | None, optional
        :return: The found default value or None.
        :rtype: Any | None
        """
        result = None
        if platform is not None:
            result = self.get(f"{platform.value}.{component}.{attr}")
        elif self.default_platform is not None:
            result = self.get(f"{self.default_platform.value}.{component}.{attr}")

        if result is None:
            # if there is no platform-specific default, look for a global default value
            result = self.get(f"Global.{component}.{attr}")
        return result

    def delete_config(self, priority: int) -> bool:
        """Deletes the configuration with the given priority.

        :param priority: The priority of the configuration to delete.
        :return: True if the configuration was deleted, False if no configuration with the given priority was found.
        """
        for i, (pri, _) in enumerate(self.__configs):
            if pri == priority:
                del self.__configs[i]
                return True
        return False

    def load_config(self, config_file: str, priority: int = 0) -> bool:
        """Loads the configuration from a yaml file.

        If a configuration with a higher priority has a value at the same path, it will be used instead.
        If multiple configurations have the same priority, the existing configuration will be overwritten.

        :param config_file: The path to the configuration file.
        :param priority: The priority of the configuration.
        """
        if priority < 0:
            logging.error("Priority must be greater than 0")
            return False
        with open(config_file, "r", encoding="utf8") as file:
            parsed = yaml.load(file, Loader=yaml.FullLoader)
        rfind = config_file.rfind("/")
        parsed = self._crawl_and_replace(parsed, config_file[:rfind] if rfind != -1 else ".")
        self.__insert_config(parsed, priority)
        return True

    def __get_from_config(self, key: str, config: dict) -> Any | None:
        key_path = key.split(".")
        while len(key_path) > 0:
            key = key_path.pop(0)
            if key.isdigit():
                config = config[int(key)]
            elif key in config:
                config = config[key]
            else:
                return None
        return config

    def __insert_config(self, config: dict, priority: int) -> None:
        """Inserts the configuration into the list of configurations at the correct position,
        according to descending priority.
        """
        for i, (pri, _) in enumerate(self.__configs):
            if pri == priority:
                # Overwrite existing configuration
                self.__configs[i] = (priority, config)
                return
            if pri < priority:
                # Insert new configuration
                self.__configs.insert(i, (priority, config))
                return
        self.__configs.append((priority, config))

    def _crawl_and_replace(
        self,
        config_part: Any,
        directory: str = ".",
    ) -> Any:
        """Crawls through the configuration and replaces every occurance of the "<file:path>"
        tag with the content of the file.

        :param config_part: The configuration to crawl through.
        :param directory: The relative directory of the configuration file.
        :return: The configuration with the replaced tags if applicable.
        """
        if isinstance(config_part, str) and _REGEX_FILE_TAG.match(config_part):
            try:
                with open(
                    f"{directory}/{_REGEX_FILE_TAG.match(config_part).group(1)}",  # type: ignore
                    "r",
                    encoding="utf8",
                ) as file:
                    return yaml.load(file, Loader=yaml.FullLoader)
            except FileNotFoundError:
                logging.error("Could not find file %s", config_part)
                return config_part
        elif isinstance(config_part, dict):
            for key in config_part:
                config_part[key] = self._crawl_and_replace(config_part[key], directory)
        elif isinstance(config_part, list):
            for i, c in enumerate(config_part):
                config_part[i] = self._crawl_and_replace(c, directory)
        return config_part
