"""
Scraper for Knesset private and government bills (הצעות חוק).
Sources:
  - Private bills:    https://main.knesset.gov.il/activity/legislation/pages/privatebills.aspx
  - Government bills: https://main.knesset.gov.il/activity/legislation/pages/governmentbills.aspx

The Knesset site is .NET/SharePoint with heavy JS rendering.
We fetch the JSON data that the page's internal API exposes, which is
accessible without JavaScript via the OData-style endpoints below.
"""

import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
}

# Knesset OData API for bills (publicly accessible, no auth required)
KNESSET_ODATA_BASE = "https://knesset.gov.il/Odata/ParliamentInfo.svc"
PRIVATE_BILLS_URL = f"{KNESSET_ODATA_BASE}/KNS_Bill()?$filter=BillTypeID eq 54&$orderby=LastUpdatedDate desc&$top=50&$format=json"
GOV_BILLS_URL = f"{KNESSET_ODATA_BASE}/KNS_Bill()?$filter=BillTypeID eq 53&$orderby=LastUpdatedDate desc&$top=50&$format=json"

# Fallback: Knesset data portal RSS-style page
KNESSET_BILLS_PAGE = "https://main.knesset.gov.il/activity/legislation/pages/privatebills.aspx"


def _parse_date(raw: str | None) -> str | None:
    if not raw:
        return None
    # OData dates come as /Date(1234567890000)/
    if raw.startswith("/Date("):
        ts = int(raw[6:-2]) // 1000
        return datetime.utcfromtimestamp(ts).strftime("%d/%m/%Y")
    return raw[:10]


def _fetch_odata(url: str) -> List[Dict[str, Any]]:
    try:
        resp = httpx.get(url, headers=HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        data = resp.json()
        return data.get("value", [])
    except Exception as e:
        print(f"[knesset_bills] OData fetch failed for {url}: {e}")
        return []


def _fallback_html_bills() -> List[Dict[str, Any]]:
    """Parse the Knesset bills HTML page as a last resort."""
    results = []
    try:
        resp = httpx.get(KNESSET_BILLS_PAGE, headers=HEADERS, timeout=30, follow_redirects=True)
        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("table tr")
        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) >= 3:
                results.append({
                    "title": cells[0].get_text(strip=True),
                    "case_number": cells[1].get_text(strip=True),
                    "pub_date": cells[2].get_text(strip=True),
                    "court": "כנסת ישראל",
                    "type": "bill",
                    "scraped_from": "knesset",
                })
    except Exception as e:
        print(f"[knesset_bills] HTML fallback failed: {e}")
    return results


def scrape_bills() -> List[Dict[str, Any]]:
    """Return a list of dicts ready to be inserted as Document rows."""
    results = []

    for url, bill_label in [
        (PRIVATE_BILLS_URL, "הצעת חוק פרטית"),
        (GOV_BILLS_URL, "הצעת חוק ממשלתית"),
    ]:
        records = _fetch_odata(url)
        for r in records:
            title = r.get("Name") or r.get("SubTypeDesc") or "הצעת חוק"
            bill_num = r.get("BillID") or ""
            results.append({
                "type": "bill",
                "title": title,
                "summary": f"{bill_label} – {r.get('StatusDesc', '')}".strip(" –"),
                "case_number": str(bill_num) if bill_num else None,
                "court": "כנסת ישראל",
                "judge": None,
                "law_area": r.get("SubTypeDesc", ""),
                "urgency": "low",
                "source_url": (
                    f"https://main.knesset.gov.il/activity/legislation/Laws/Pages/LawBill.aspx?t=lawbill&lawitemid={bill_num}"
                    if bill_num else None
                ),
                "pub_date": _parse_date(r.get("LastUpdatedDate")),
                "raw_content": None,
                "scraped_from": "knesset",
            })

    if not results:
        # try HTML fallback
        results = _fallback_html_bills()

    return results
