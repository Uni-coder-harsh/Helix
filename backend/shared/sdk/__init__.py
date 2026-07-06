from abc import ABC, abstractmethod
from typing import Any, Dict


class HelixPlugin(ABC):
    """Abstract Base Class representing a Helix Third-Party Plugin.

    All custom sandboxed plugins must subclass this interface.
    """

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> None:
        """Initializes the plugin with configuration parameters.

        Args:
            config: Key-value configuration dict loaded from helix_platform.
        """
        pass

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Executes the plugin hooks logic within the isolated runtime.

        Args:
            context: Contextual payload representing the active trigger event.

        Returns:
            Dict containing the execution outputs.
        """
        pass
