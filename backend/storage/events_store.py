from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4


class EventsStore:
    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _read(self) -> List[Dict[str, Any]]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        return data if isinstance(data, list) else []

    def _write(self, items: List[Dict[str, Any]]) -> None:
        self.path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list(self) -> List[Dict[str, Any]]:
        return deepcopy(self._read())

    def get_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        for item in self._read():
            if item.get("id") == event_id:
                return deepcopy(item)
        return None

    def get_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        for item in self._read():
            if item.get("slug") == slug:
                return deepcopy(item)
        return None

    def insert(self, item: Dict[str, Any]) -> Dict[str, Any]:
        rows = self._read()
        row = deepcopy(item)
        row.setdefault("id", str(uuid4()))
        rows.insert(0, row)
        self._write(rows)
        return deepcopy(row)

    def update(self, event_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rows = self._read()
        for idx, row in enumerate(rows):
            if row.get("id") != event_id:
                continue
            updated = {**row, **deepcopy(patch)}
            rows[idx] = updated
            self._write(rows)
            return deepcopy(updated)
        return None

    def replace_all(self, items: List[Dict[str, Any]]) -> None:
        rows: List[Dict[str, Any]] = []
        for item in items:
            row = deepcopy(item)
            row.setdefault("id", str(uuid4()))
            rows.append(row)
        self._write(rows)
