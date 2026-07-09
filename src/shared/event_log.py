from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.shared.schemas import to_plain_dict


class JsonlLogger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")

    def write(self, event: Any) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(to_plain_dict(event), ensure_ascii=False, sort_keys=True))
            f.write("\n")

