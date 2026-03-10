"""
Scraper for enacted Israeli laws (חקיקה ראשית) published in the Reshumot
(Official Gazette).

Source: Knesset OData API – KNS_Law table
"""

import httpx
from datetime import datetime
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
}

KNESSET_ODATA_BASE = "https://knesset.gov.il/Odata/ParliamentInfo.svc"
LAWS_URL = (
    f"{KNESSET_ODATA_BASE}/KNS_Law()"
    "?$orderby=LastUpdatedDate desc&$top=50&$format=json"
)


def _parse_date(raw: str | None) -> str | None:
    if not raw:
        return None
    if raw.startswith("/Date("):
        ts = int(raw[6:-2]) // 1000
        return datetime.utcfromtimestamp(ts).strftime("%d/%m/%Y")
    return raw[:10]


def scrape_laws() -> List[Dict[str, Any]]:
    """Return enacted laws as Document-ready dicts."""
    results = []
    try:
        resp = httpx.get(LAWS_URL, headers=HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        records = resp.json().get("value", [])
    except Exception as e:
        print(f"[knesset_laws] Fetch failed: {e}")
        return []

    for r in records:
        law_id = r.get("LawID") or ""
        name = r.get("Name") or "חוק"
        results.append({
            "type": "legislation",
            "title": name,
            "summary": f"חוק שנחקק | מספר: {law_id}",
            "case_number": str(law_id) if law_id else None,
            "court": "כנסת ישראל",
            "judge": None,
            "law_area": None,
            "urgency": "low",
            "source_url": (
                f"https://main.knesset.gov.il/activity/legislation/Laws/Pages/LawPrimary.aspx?t=lawlaws&lawitemid={law_id}"
                if law_id else None
            ),
            "pub_date": _parse_date(r.get("LastUpdatedDate")),
            "raw_content": None,
            "scraped_from": "knesset",
        })

    return results
