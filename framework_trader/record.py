import json
import os
from typing import Any, Mapping

from benedict import benedict
from pydantic import Field
from pydantic.dataclasses import dataclass

from framework_trader.common.constants import DEFAULT_RECORD_PATH


@dataclass
class Recorder:
    """
    Recorder to store and save data to disk.

    Attributes:
        record: Mapping of data to be stored.
        save_path: Path to save the data to.
    """

    record: Mapping[Any, Any] = Field(default_factory=benedict)
    save_path: os.PathLike = Field(default=DEFAULT_RECORD_PATH)

    def __getitem__(self, key: Any) -> Any:
        """
        Get the value associated with the given key.

        Args:
            key: The key to retrieve.

        Returns:
            The value associated with the key or None if the key is not found.
        """
        return self.record.get(key, None)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set the value associated with the given key.

        Args:
            key: The key to set.
            value: The value to set.
        """
        self.record[key] = value

    def save_to_disk(self) -> None:
        """
        Save the record to disk.
        """
        with open(self.save_path, "w") as f:
            json.dump(self.record, f, indent=4, default=str)
