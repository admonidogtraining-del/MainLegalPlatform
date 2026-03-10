"""
Scraper for Nevo Legal Database (נבו) – https://www.nevo.co.il/

Nevo is Israel's largest legal database. The following sections are
publicly accessible without authentication:
  - Primary legislation index (law_html/)
  - Recent additions RSS feed
  - Public search results page

We fetch the public legislation listing and the RSS feed.
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml",
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
    "Referer": "https://www.nevo.co.il/",
}

BASE_URL = "https://www.nevo.co.il"
# Public RSS feeds (no auth required)
RSS_LAWS = f"{BASE_URL}/rss/laws.aspx"
RSS_VERDICTS = f"{BASE_URL}/rss/verdicts.aspx"
# Public legislation listing
LAW_INDEX_URL = f"{BASE_URL}/law_html/law0/"


def _normalise_url(href: str | None) -> str | None:
    if not href:
        return None
    href = href.strip()
    if href.startswith("http"):
        return href
    return BASE_URL + ("" if href.startswith("/") else "/") + href


def _parse_date(raw: str | None) -> str | None:
    """Accept RFC 2822 (Tue, 11 Mar 2025 ...) or YYYY-MM-DD, return DD/MM/YYYY."""
    if not raw:
        return None
    raw = raw.strip()
    # RFC 2822 – take the date portion
    parts = raw.split(",")
    if len(parts) == 2:
        raw = parts[1].strip()
    # "11 Mar 2025 ..."
    months = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
    }
    toks = raw.split()
    if len(toks) >= 3 and toks[1] in months:
        return f"{toks[0].zfill(2)}/{months[toks[1]]}/{toks[2]}"
    # YYYY-MM-DD
    if len(raw) >= 10 and raw[4] == "-":
        y, m, d = raw[:10].split("-")
        return f"{d}/{m}/{y}"
    # DD/MM/YYYY already
    return raw[:10] if len(raw) >= 10 else raw


def _scrape_rss(feed_url: str, doc_type: str, source_label: str) -> List[Dict[str, Any]]:
    """Parse an RSS feed from Nevo and return document-ready dicts."""
    results: List[Dict[str, Any]] = []
    try:
        resp = httpx.get(feed_url, headers=HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # Handle both RSS 2.0 (<item>) and Atom (<entry>)
        items = root.findall(".//item") or root.findall(".//atom:entry", ns)

        for item in items[:50]:
            def _text(tag: str) -> str | None:
                el = item.find(tag) or item.find(f"atom:{tag}", ns)
                return el.text.strip() if el is not None and el.text else None

            title = _text("title") or ""
            link = _text("link") or ""
            if not link:
                link_el = item.find("atom:link", ns)
                link = (link_el.get("href") if link_el is not None else None) or ""
            pub_date = _text("pubDate") or _text("published") or _text("updated") or ""
            description = _text("description") or _text("summary") or ""

            # Strip HTML from description if present
            if "<" in description:
                description = BeautifulSoup(description, "lxml").get_text(separator=" ", strip=True)

            if not title:
                continue

            results.append({
                "type": doc_type,
                "title": title,
                "summary": description[:400] if description else f"{source_label} | נבו",
                "case_number": None,
                "court": "נבו" if doc_type == "ruling" else "כנסת ישראל",
                "judge": None,
                "law_area": None,
                "urgency": "low",
                "source_url": _normalise_url(link) if link else None,
                "pub_date": _parse_date(pub_date),
                "raw_content": None,
                "scraped_from": "nevo",
            })
    except ET.ParseError as e:
        print(f"[nevo] RSS parse error for {feed_url}: {e}")
    except Exception as e:
        print(f"[nevo] RSS fetch failed for {feed_url}: {e}")
    return results


def _scrape_law_index() -> List[Dict[str, Any]]:
    """
    Fallback: scrape the public Nevo legislation alphabetical index.
    Returns recently listed law entries.
    """
    results: List[Dict[str, Any]] = []
    try:
        resp = httpx.get(LAW_INDEX_URL, headers=HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        links = soup.select("a[href*='law_html']")
        for a in links[:60]:
            title = a.get_text(strip=True)
            if not title:
                continue
            url = _normalise_url(a.get("href"))
            results.append({
                "type": "legislation",
                "title": title,
                "summary": f"חקיקה ראשית | נבו",
                "case_number": None,
                "court": "כנסת ישראל",
                "judge": None,
                "law_area": None,
                "urgency": "low",
                "source_url": url,
                "pub_date": None,
                "raw_content": None,
                "scraped_from": "nevo",
            })
    except Exception as e:
        print(f"[nevo] law index scrape failed: {e}")
    return results


def scrape_nevo() -> List[Dict[str, Any]]:
    """Return documents from Nevo (legislation + rulings), ready for insertion."""
    results: List[Dict[str, Any]] = []

    # Primary: RSS feeds
    results += _scrape_rss(RSS_LAWS, "legislation", "חקיקה")
    results += _scrape_rss(RSS_VERDICTS, "ruling", "פסיקה")

    # Fallback to HTML index if RSS returned nothing useful
    if len(results) < 5:
        results += _scrape_law_index()

    return results
