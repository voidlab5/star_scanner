#!/usr/bin/env python3
"""
StarBT Installment Finder
Scrapes starbt.ro/parteneri for the watched stores and prints their installment counts.

Usage:
    python star_scanner.py

Requirements:
    pip install requests beautifulsoup4
"""

import re
import sys
import time
import logging

import requests
from bs4 import BeautifulSoup

# ── Stores to watch ───────────────────────────────────────────────────────────

WATCHED_STORES = [
    "emag",
    "altex",
    "flanco",
    "vexio",
    "evomag",
    "pcgarage",
    "cel.ro",
    "media galaxy",
    "carturesti",
    "elefant",
    "soundcreation",
]

# ── Settings ──────────────────────────────────────────────────────────────────

BASE_URL            = "https://www.starbt.ro/parteneri"
DELAY_BETWEEN_PAGES = 0.3
RETRY_DELAYS        = [5, 15, 30]
REQUEST_TIMEOUT     = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
log = logging.getLogger(__name__)

# ── HTTP helpers ──────────────────────────────────────────────────────────────

def fetch_with_retry(session: requests.Session, url: str, params: dict) -> requests.Response:
    last_exc = None
    for attempt, wait in enumerate([0] + RETRY_DELAYS, start=1):
        if wait:
            time.sleep(wait)
        try:
            resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 60))
                log.warning(f"Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                last_exc = requests.HTTPError("429")
                continue

            if resp.status_code == 503:
                log.warning("503 Service Unavailable. Will retry...")
                last_exc = requests.HTTPError("503")
                continue

            resp.raise_for_status()
            return resp

        except requests.ConnectionError as e:
            log.warning(f"Connection error: {e}")
            last_exc = e
        except requests.Timeout:
            log.warning(f"Timeout after {REQUEST_TIMEOUT}s")
            last_exc = TimeoutError()
        except requests.HTTPError as e:
            log.warning(f"HTTP error: {e}")
            last_exc = e

    raise RuntimeError(
        f"Failed to fetch {url} after {len(RETRY_DELAYS)+1} attempts. Last: {last_exc}"
    )

# ── Pagination ────────────────────────────────────────────────────────────────

def get_total_pages(soup: BeautifulSoup) -> int:
    candidates = set()

    for a in soup.select("a[href]"):
        m = re.search(r"[?&]page=(\d+)", a.get("href", ""))
        if m:
            candidates.add(int(m.group(1)))

    for el in soup.find_all(attrs={"onclick": True}):
        for m in re.finditer(r"\bpage[=\s(,]+(\d+)", el["onclick"], re.IGNORECASE):
            candidates.add(int(m.group(1)))

    for el in soup.find_all(attrs={"data-page": True}):
        try:
            candidates.add(int(el["data-page"]))
        except ValueError:
            pass

    for el in soup.select("nav a, .pagination a, ul.pages a, [class*='pag'] a"):
        txt = el.get_text(strip=True)
        if txt.isdigit():
            candidates.add(int(txt))

    return max(candidates) if candidates else 1

# ── Parsing ───────────────────────────────────────────────────────────────────

def extract_installments(text: str) -> int | None:
    m = re.search(r"Rate\s+fără\s+dobândă[^0-9]*(\d+)", text, re.IGNORECASE)
    return int(m.group(1)) if m else None


def parse_stores_from_soup(soup: BeautifulSoup) -> list[dict]:
    links = (
        soup.select("a[href*='/parteneri/']")
        or soup.select("a[href*='starbt.ro/parteneri']")
        or soup.find_all("a", href=True)
    )

    seen    = set()
    results = []

    for link in links:
        href = link.get("href", "")
        if href.rstrip("/").endswith("/parteneri"):
            continue
        if href in seen:
            continue
        seen.add(href)

        full_text = link.get_text(" ", strip=True)

        # Strip markdown-link format [text](url) → text
        full_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', full_text)

        # Strip everything from "Rate fără" onward to isolate name (+ category)
        pre_rate = re.split(r"Rate\s+fără", full_text, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        parts    = pre_rate.split(" - ")
        name     = parts[0].strip() if parts else pre_rate[:60]

        # Deduplicate doubled names e.g. "EMAGEEMAG" → "EMAG"
        half = len(name) // 2
        if len(name) % 2 == 0 and name[:half] == name[half:]:
            name = name[:half]

        installments = extract_installments(full_text)
        url          = href if href.startswith("http") else "https://www.starbt.ro" + href

        results.append({"name": name, "installments": installments, "url": url})

    return results

# ── Fetching ──────────────────────────────────────────────────────────────────

def fetch_all_pages(session: requests.Session, params_base: dict) -> list[dict]:
    resp  = fetch_with_retry(session, BASE_URL, {**params_base, "page": 1})
    soup  = BeautifulSoup(resp.text, "html.parser")
    total = get_total_pages(soup)
    stores = parse_stores_from_soup(soup)

    for page in range(2, total + 1):
        time.sleep(DELAY_BETWEEN_PAGES)
        resp = fetch_with_retry(session, BASE_URL, {**params_base, "page": page})
        soup = BeautifulSoup(resp.text, "html.parser")
        stores.extend(parse_stores_from_soup(soup))

    return stores


def _name_matches(name: str, term: str) -> bool:
    """True only if the store name belongs to the searched brand.

    Strips leading 'www.' so 'www.emag.ro' matches 'emag', then requires
    the name to START with the search term — preventing false positives like
    kafemag/ledemag for 'emag', or MALTEX/WALTEX/SOTO ALTEX for 'altex'.
    """
    clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', name)
    clean = re.sub(r'^www\.', '', clean.strip(), flags=re.IGNORECASE).lower()
    t     = term.lower().strip()
    return clean.replace(" ", "").startswith(t.replace(" ", ""))


def search_store(session: requests.Session, search_term: str) -> list[dict]:
    params = {
        "categorii": "",
        "tip":       "",
        "plata":     "rate",
        "search":    search_term,
    }
    all_stores = fetch_all_pages(session, params)
    return [s for s in all_stores if _name_matches(s["name"], search_term)]

# ── Output ────────────────────────────────────────────────────────────────────

def print_summary(results_by_store: dict[str, list[dict]]):
    print(f"\n{'='*50}")
    print(f"  Watched stores — current installment counts")
    print(f"{'='*50}\n")

    for search_term, stores in sorted(results_by_store.items()):
        if not stores:
            print(f"  ({search_term} — not found)")
            continue
        for s in sorted(stores, key=lambda x: x["name"].lower()):
            rate_str = f"{s['installments']} rate" if s["installments"] is not None else "—"
            print(f"  {s['name']:<35} {rate_str}")
    print()

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not WATCHED_STORES:
        log.error("WATCHED_STORES is empty — nothing to search.")
        sys.exit(1)

    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        results_by_store: dict[str, list[dict]] = {}
        for term in WATCHED_STORES:
            log.info(f"Searching: {term}")
            results_by_store[term] = search_store(session, term)

        print_summary(results_by_store)

    except RuntimeError as e:
        log.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
