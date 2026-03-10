from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class ExtractConfig(BaseModel):
    css: list[str] = Field(default_factory=list)
    xpath: list[str] = Field(default_factory=list)
    regex: list[str] = Field(default_factory=list)
    return_html: bool = False


class FetchRequest(BaseModel):
    url: HttpUrl
    method: str = Field(default="GET", pattern="^(GET|POST|PUT|DELETE)$")
    headers: dict[str, str] | None = None
    cookies: dict[str, str] | None = None
    proxy: str | None = None
    timeout: int = Field(default=30, ge=1, le=120)
    impersonate: str | None = None
    follow_redirects: bool = True
    params: dict[str, str] | None = None
    body: dict[str, Any] | None = None
    json_body: dict[str, Any] | None = None
    extract: ExtractConfig | None = None


class DynamicRequest(BaseModel):
    url: HttpUrl
    headless: bool = True
    disable_resources: bool = False
    network_idle: bool = True
    timeout: int = Field(default=30, ge=1, le=120)
    wait_selector: str | None = None
    wait_selector_state: str = Field(default="attached", pattern="^(attached|visible)$")
    cookies: dict[str, str] | None = None
    proxy: str | None = None
    extract: ExtractConfig | None = None


class StealthRequest(BaseModel):
    url: HttpUrl
    headless: bool = True
    timeout: int = Field(default=60, ge=1, le=180)
    wait_selector: str | None = None
    wait_selector_state: str = Field(default="attached", pattern="^(attached|visible)$")
    cookies: dict[str, str] | None = None
    proxy: str | None = None
    solve_cloudflare: bool = False
    humanize: bool = False
    block_webrtc: bool = False
    allow_webgl: bool = False
    disable_ads: bool = False
    os_randomize: bool = False
    geoip: bool = False
    disable_resources: bool = False
    network_idle: bool = False
    extract: ExtractConfig | None = None
