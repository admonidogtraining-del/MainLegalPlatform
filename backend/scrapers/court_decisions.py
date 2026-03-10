"""
Scraper for Israeli court decisions (פסיקה).

Sources:
  1. Supreme Court public search API – supreme.court.gov.il
  2. Elyon1 (Israeli courts authority) – elyon1.court.gov.il

The Supreme Court exposes a JSON search endpoint used by their public
search UI. We query it for the most recent decisions.

Public access confirmed by Israeli Supreme Court ruling (Nov 2015):
blocking indexing of public court decisions is unlawful.
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html",
    "Accept-Language": "he-IL,he;q=0.9",
}

# Supreme Court public search API (used by their own search page)
SUPREME_SEARCH_URL = "https://supreme.court.gov.il/sites/en/_layouts/15/Beit_Mishpat.Supreme.Search/SearchResults.aspx/GetResults"

# Elyon1 – public court decisions portal
ELYON1_SEARCH_URL = "https://elyon1.court.gov.il/heb/verdict_search/verdict_search.asp"
ELYON1_BASE = "https://elyon1.court.gov.il"

COURT_TYPE_MAP = {
    "1": "בית המשפט העליון",
    "2": "בית משפט מחוזי",
    "3": "בית משפט שלום",
    "4": "בית הדין לעבודה",
}

AREA_MAP = {
    "civil": "אזרחי",
    "criminal": "פלילי",
    "administrative": "מנהלי",
    "labour": "עבודה",
    "family": "משפחה",
}


def _scrape_elyon1() -> List[Dict[str, Any]]:
    """Scrape recent decisions from the elyon1 public portal."""
    results = []
    try:
        # Query with empty form to get recent results
        resp = httpx.post(
            ELYON1_SEARCH_URL,
            data={
                "btnSearch": "חיפוש",
                "txtCaseNum": "",
                "txtYear": "",
                "ddlCourt": "0",
                "txtFromDate": "",
                "txtToDate": "",
            },
            headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
            follow_redirects=True,
        )
        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("table.resultsTable tr, table tr")

        for row in rows[1:51]:  # up to 50 results
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            case_num = cells[0].get_text(strip=True)
            court_raw = cells[1].get_text(strip=True)
            date_raw = cells[2].get_text(strip=True)
            link_tag = cells[3].find("a")
            title = link_tag.get_text(strip=True) if link_tag else cells[3].get_text(strip=True)
            url = (ELYON1_BASE + link_tag["href"]) if link_tag and link_tag.get("href") else None

            results.append({
                "type": "ruling",
                "title": title or case_num,
                "summary": f"פסק דין | {court_raw}",
                "case_number": case_num,
                "court": court_raw or "בית משפט",
                "judge": None,
                "law_area": None,
                "urgency": "low",
                "source_url": url,
                "pub_date": date_raw,
                "raw_content": None,
                "scraped_from": "elyon1",
            })
    except Exception as e:
        print(f"[court_decisions] elyon1 scrape failed: {e}")

    return results


def _scrape_supreme_court() -> List[Dict[str, Any]]:
    """
    Try the Supreme Court public website for recent decisions.
    Falls back gracefully if the endpoint structure has changed.
    """
    results = []
    try:
        resp = httpx.get(
            "https://supreme.court.gov.il/sites/he/verdicts/Pages/recentverdicts.aspx",
            headers=HEADERS,
            timeout=30,
            follow_redirects=True,
        )
        soup = BeautifulSoup(resp.text, "lxml")

        # Look for verdict rows in any table or list structure
        items = soup.select(".ms-listviewtable tr, table.verdictTable tr, li.verdict-item")
        for item in items[1:31]:
            cells = item.find_all("td")
            if not cells:
                continue
            title = cells[0].get_text(strip=True) if cells else ""
            date_raw = cells[-1].get_text(strip=True) if len(cells) > 1 else ""
            link = item.find("a")
            url = link["href"] if link and link.get("href") else None
            if url and not url.startswith("http"):
                url = "https://supreme.court.gov.il" + url

            if not title:
                continue

            results.append({
                "type": "ruling",
                "title": title,
                "summary": "פסק דין – בית המשפט העליון",
                "case_number": None,
                "court": "בית המשפט העליון",
                "judge": None,
                "law_area": None,
                "urgency": "low",
                "source_url": url,
                "pub_date": date_raw,
                "raw_content": None,
                "scraped_from": "supreme",
            })
    except Exception as e:
        print(f"[court_decisions] supreme court scrape failed: {e}")

    return results


def scrape_court_decisions() -> List[Dict[str, Any]]:
    """Aggregate court decisions from all available sources."""
    results = _scrape_supreme_court()
    if len(results) < 5:
        results += _scrape_elyon1()
    return results
