from __future__ import annotations

import re
import time
from typing import Any

from scrapling import AsyncFetcher, StealthyFetcher
from scrapling.fetchers import DynamicFetcher

from app.schemas.request import DynamicRequest, ExtractConfig, FetchRequest, StealthRequest
from app.schemas.response import ScrapeResponse


def _extract(response: Any, config: ExtractConfig) -> dict[str, dict[str, list[str]]]:
    result: dict[str, dict[str, list[str]]] = {}

    if config.css:
        css_results: dict[str, list[str]] = {}
        for selector in config.css:
            css_results[selector] = [str(t) for t in response.css(selector).getall()]
        result["css"] = css_results

    if config.xpath:
        xpath_results: dict[str, list[str]] = {}
        for expr in config.xpath:
            xpath_results[expr] = [str(t) for t in response.xpath(expr).getall()]
        result["xpath"] = xpath_results

    if config.regex:
        html = response.body.decode(response.encoding, errors="replace")
        regex_results: dict[str, list[str]] = {}
        for pattern in config.regex:
            regex_results[pattern] = re.findall(pattern, html)
        result["regex"] = regex_results

    return result


def _build_response(response: Any, elapsed_ms: int, extract: ExtractConfig | None) -> ScrapeResponse:
    cookies = response.cookies
    if isinstance(cookies, (list, tuple)):
        merged: dict[str, str] = {}
        for d in cookies:
            if isinstance(d, dict):
                merged.update(d)
        cookies = merged
    elif not isinstance(cookies, dict):
        cookies = {}

    headers = dict(response.headers) if response.headers else {}

    return_html = extract.return_html if extract else True
    html = response.body.decode(response.encoding, errors="replace") if return_html else None
    extracted = _extract(response, extract) if extract else None

    return ScrapeResponse(
        status=response.status,
        reason=response.reason,
        url=str(response.url),
        headers=headers,
        cookies=cookies,
        html=html,
        extracted=extracted,
        elapsed_ms=elapsed_ms,
    )


async def fetch_static(req: FetchRequest) -> ScrapeResponse:
    kwargs: dict[str, Any] = {}
    if req.headers:
        kwargs["headers"] = req.headers
    if req.cookies:
        kwargs["cookies"] = req.cookies
    if req.proxy:
        kwargs["proxy"] = req.proxy
    if req.impersonate:
        kwargs["impersonate"] = req.impersonate
    if req.params:
        kwargs["params"] = req.params
    kwargs["timeout"] = req.timeout
    kwargs["follow_redirects"] = req.follow_redirects

    method = req.method.upper()
    url = str(req.url)

    start = time.monotonic()

    if method == "GET":
        response = await AsyncFetcher.get(url, **kwargs)
    elif method == "POST":
        if req.json_body:
            kwargs["json"] = req.json_body
        elif req.body:
            kwargs["data"] = req.body
        response = await AsyncFetcher.post(url, **kwargs)
    elif method == "PUT":
        if req.json_body:
            kwargs["json"] = req.json_body
        elif req.body:
            kwargs["data"] = req.body
        response = await AsyncFetcher.put(url, **kwargs)
    elif method == "DELETE":
        response = await AsyncFetcher.delete(url, **kwargs)
    else:
        raise ValueError(f"Unsupported method: {method}")

    elapsed_ms = int((time.monotonic() - start) * 1000)
    return _build_response(response, elapsed_ms, req.extract)


async def fetch_dynamic(req: DynamicRequest) -> ScrapeResponse:
    kwargs: dict[str, Any] = {
        "headless": req.headless,
        "disable_resources": req.disable_resources,
        "network_idle": req.network_idle,
        "timeout": req.timeout,
    }
    if req.wait_selector:
        kwargs["wait_selector"] = req.wait_selector
        kwargs["wait_selector_state"] = req.wait_selector_state
    if req.cookies:
        kwargs["cookies"] = [{"name": k, "value": v} for k, v in req.cookies.items()]
    if req.proxy:
        kwargs["proxy"] = req.proxy

    start = time.monotonic()
    response = await DynamicFetcher.async_fetch(str(req.url), **kwargs)
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return _build_response(response, elapsed_ms, req.extract)


async def fetch_stealth(req: StealthRequest) -> ScrapeResponse:
    kwargs: dict[str, Any] = {
        "headless": req.headless,
        "timeout": req.timeout,
        "block_webrtc": req.block_webrtc,
        "allow_webgl": req.allow_webgl,
        "disable_resources": req.disable_resources,
        "network_idle": req.network_idle,
    }
    if req.wait_selector:
        kwargs["wait_selector"] = req.wait_selector
        kwargs["wait_selector_state"] = req.wait_selector_state
    if req.cookies:
        kwargs["cookies"] = [{"name": k, "value": v} for k, v in req.cookies.items()]
    if req.proxy:
        kwargs["proxy"] = req.proxy
    if req.solve_cloudflare:
        kwargs["solve_cloudflare"] = True
    if req.humanize:
        kwargs["humanize"] = True
    if req.disable_ads:
        kwargs["disable_ads"] = True
    if req.os_randomize:
        kwargs["os_randomize"] = True
    if req.geoip:
        kwargs["geoip"] = True

    start = time.monotonic()
    response = await StealthyFetcher.async_fetch(str(req.url), **kwargs)
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return _build_response(response, elapsed_ms, req.extract)
