"""
Scraper for Psikat Din (פסיקת דין) – https://www.psakdin.co.il/

Psikat Din aggregates Israeli court decisions from all levels.
We scrape their publicly accessible recent-decisions listing.
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
    "Referer": "https://www.psakdin.co.il/",
}

BASE_URL = "https://www.psakdin.co.il"
RECENT_URL = f"{BASE_URL}/"
SEARCH_URL = f"{BASE_URL}/Search"


def _normalise_url(href: str | None) -> str | None:
    if not href:
        return None
    href = href.strip()
    if href.startswith("http"):
        return href
    return BASE_URL + ("" if href.startswith("/") else "/") + href


def _parse_date(raw: str | None) -> str | None:
    """Accept DD/MM/YYYY or YYYY-MM-DD and normalise to DD/MM/YYYY."""
    if not raw:
        return None
    raw = raw.strip()
    if len(raw) == 10 and raw[4] == "-":
        y, m, d = raw.split("-")
        return f"{d}/{m}/{y}"
    return raw


def _scrape_recent() -> List[Dict[str, Any]]:
    """Scrape the Psikat Din home / recent-decisions page."""
    results: List[Dict[str, Any]] = []
    try:
        resp = httpx.get(RECENT_URL, headers=HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # The site renders verdict cards / rows – try common selectors
        items = (
            soup.select("div.verdict-item, div.ruling-item, article.verdict, "
                        "tr.verdict-row, div.card, li.list-group-item")
        )

        for item in items[:50]:
            # Title
            title_tag = item.select_one("h2, h3, h4, .title, .verdict-title, a[href*='verdict'], a[href*='Verdict']")
            title = title_tag.get_text(strip=True) if title_tag else ""

            # Link
            link_tag = title_tag if (title_tag and title_tag.name == "a") else item.find("a")
            url = _normalise_url(link_tag.get("href") if link_tag else None)

            # Date
            date_tag = item.select_one(".date, .pub-date, time, .verdict-date, td.date")
            date_raw = date_tag.get_text(strip=True) if date_tag else None
            if date_tag and date_tag.get("datetime"):
                date_raw = date_tag["datetime"][:10]

            # Court
            court_tag = item.select_one(".court, .court-name, .bet-mishpat")
            court = court_tag.get_text(strip=True) if court_tag else "בית משפט"

            # Case number
            case_tag = item.select_one(".case-number, .mispar-tik, .tik")
            case_num = case_tag.get_text(strip=True) if case_tag else None

            # Judge
            judge_tag = item.select_one(".judge, .shofet, .dayan")
            judge = judge_tag.get_text(strip=True) if judge_tag else None

            if not title and not url:
                continue

            results.append({
                "type": "ruling",
                "title": title or case_num or "פסק דין",
                "summary": f"פסק דין | {court}",
                "case_number": case_num,
                "court": court,
                "judge": judge,
                "law_area": None,
                "urgency": "low",
                "source_url": url,
                "pub_date": _parse_date(date_raw),
                "raw_content": None,
                "scraped_from": "psakdin",
            })
    except Exception as e:
        print(f"[psakdin] recent page scrape failed: {e}")

    return results


def _scrape_search_page() -> List[Dict[str, Any]]:
    """
    Fallback: submit an empty search on the Psikat Din search page
    and parse the results table.
    """
    results: List[Dict[str, Any]] = []
    try:
        resp = httpx.get(SEARCH_URL, headers=HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        rows = soup.select("table tr, div.search-result")
        for row in rows[1:51]:
            cells = row.find_all("td")
            if len(cells) < 3:
                # div-based result
                title_tag = row.select_one("a, .title, h3, h4")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                url = _normalise_url(title_tag.get("href") if title_tag.name == "a" else
                                     (title_tag.find("a") or {}).get("href"))
                date_tag = row.select_one(".date, time")
                results.append({
                    "type": "ruling",
                    "title": title,
                    "summary": "פסק דין | פסיקת דין",
                    "case_number": None,
                    "court": "בית משפט",
                    "judge": None,
                    "law_area": None,
                    "urgency": "low",
                    "source_url": url,
                    "pub_date": _parse_date(date_tag.get_text(strip=True) if date_tag else None),
                    "raw_content": None,
                    "scraped_from": "psakdin",
                })
                continue

            # Table row
            link_tag = cells[0].find("a")
            title = link_tag.get_text(strip=True) if link_tag else cells[0].get_text(strip=True)
            url = _normalise_url(link_tag.get("href") if link_tag else None)
            court = cells[1].get_text(strip=True) if len(cells) > 1 else "בית משפט"
            date_raw = cells[2].get_text(strip=True) if len(cells) > 2 else None
            case_num = cells[3].get_text(strip=True) if len(cells) > 3 else None

            if not title:
                continue

            results.append({
                "type": "ruling",
                "title": title,
                "summary": f"פסק דין | {court}",
                "case_number": case_num,
                "court": court,
                "judge": None,
                "law_area": None,
                "urgency": "low",
                "source_url": url,
                "pub_date": _parse_date(date_raw),
                "raw_content": None,
                "scraped_from": "psakdin",
            })
    except Exception as e:
        print(f"[psakdin] search page scrape failed: {e}")

    return results


def scrape_psakdin() -> List[Dict[str, Any]]:
    """Return Psikat Din court decisions, ready to be inserted as Document rows."""
    results = _scrape_recent()
    if len(results) < 5:
        results += _scrape_search_page()
    return results
