"""IPTV playlist scraper skeleton.

This module provides a minimal structure for fetching HTML from streaming
websites and extracting stream links for playlist generation. Extend the
`SOURCES` list with site-specific parsing logic as needed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup

PLAYLIST_PATH = Path("playlist.m3u")

STREAM_LINK_PATTERNS = [
    re.compile(r"https?://[^\s'\"]+\.m3u8[^\s'\"]*", re.IGNORECASE),
    re.compile(r"https?://[^\s'\"]+/(?:stream|live)[^\s'\"]*", re.IGNORECASE),
]


@dataclass(frozen=True)
class Source:
    name: str
    url: str

    def extract_links(self, html: str) -> list[str]:
        """Default extraction uses regex over raw HTML.

        Override this method to add site-specific parsing in the future.
        """
        return extract_stream_links(html)


SOURCES: list[Source] = [
    Source(name="Toffee", url="https://toffeelive.com/en/live"),
    Source(name="Bongo", url="https://example.com/bongo"),
]


def fetch_html(url: str, timeout: int = 20) -> str:
    """Fetch HTML content for a URL."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_stream_links(html: str) -> list[str]:
    """Extract m3u8 or stream-like links from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    text_sources = [html, soup.get_text(" ")]
    links: set[str] = set()

    for text in text_sources:
        for pattern in STREAM_LINK_PATTERNS:
            links.update(pattern.findall(text))

    return sorted(links)


def format_playlist_entry(name: str, url: str) -> str:
    """Format a single playlist entry."""
    return f"#EXTINF:-1, {name}\n{url}"


def build_playlist(sources: Iterable[Source]) -> list[str]:
    """Build playlist entries from sources."""
    entries: list[str] = ["#EXTM3U"]

    for source in sources:
        html = fetch_html(source.url)
        links = source.extract_links(html)

        for index, link in enumerate(links, start=1):
            channel_name = f"{source.name} {index}"
            entries.append(format_playlist_entry(channel_name, link))

    return entries


def save_playlist(entries: Iterable[str], path: Path = PLAYLIST_PATH) -> None:
    """Save playlist entries to disk."""
    path.write_text("\n".join(entries) + "\n", encoding="utf-8")


def main() -> None:
    """Run the scraper and write the playlist."""
    entries = build_playlist(SOURCES)
    save_playlist(entries)


if __name__ == "__main__":
    main()
