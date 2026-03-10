from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ScrapeResponse(BaseModel):
    status: int
    reason: str
    url: str
    headers: dict[str, str]
    cookies: dict[str, str]
    html: str | None = None
    extracted: dict[str, dict[str, list[str]]] | None = None
    elapsed_ms: int
