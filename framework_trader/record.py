import json
import os
from typing import Any, Mapping

from benedict import benedict
from pydantic import Field
from pydantic.dataclasses import dataclass

from framework_trader.common.constants import DEFAULT_RECORD_PATH


@dataclass
class Recorder:
    record: Mapping[Any, Any] = Field(default_factory=benedict)
    save_path: os.PathLike = Field(default=DEFAULT_RECORD_PATH)

    def __getitem__(self, key: Any) -> Any:
        return self.record.get(key, None)

    def __setitem__(self, key: Any, value: Any) -> None:
        self.record[key] = value

    def save_to_disk(self) -> None:
        with open(self.save_path, "w") as f:
            json.dump(self.record, f, indent=4, default=str)
