# StarBT Installment Count Finder

A Python script that checks [starbt.ro/parteneri](https://www.starbt.ro/parteneri) and reports the current interest-free installment count for a list of watched stores.

## What it does

Banca Transilvania's StarBT card offers interest-free installments at partner stores, but the number of installments changes over time. This script automates checking the current count for the stores you care about, so you don't have to do it manually before a purchase.

Example output:

```
==================================================
  Watched stores — current installment counts
==================================================

  Altex Electro                       5 rate
  WWW.ALTEX.RO                        5 rate
  DEDEMAN                             9 rate
  www.dedeman.ro                      9 rate
  EVOMAG                              12 rate
  WWW.EVOMAG.RO                       12 rate
  eMAG                                6 rate
  WWW.EMAG.RO                         6 rate
  ...
```

## Requirements

- Python 3.10+
- [requests](https://pypi.org/project/requests/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)

```
pip install requests beautifulsoup4
```

## Usage

```
python star_scanner.py
```

## Configuration

Edit the `WATCHED_STORES` list at the top of the script to add or remove stores. Each entry is a search term — matching is case-insensitive and the script requires the store name to start with the term, so partial terms like `"emag"` will match `eMAG`, `WWW.EMAG.RO`, and `EMAG ASIGURARI`, but not unrelated stores that happen to contain the string.

```python
WATCHED_STORES = [
    "emag",
    "altex",
    "flanco",
    "dedeman",
    # add more here
]
```

Other settings near the top of the file:

| Setting | Default | Description |
|---|---|---|
| `DELAY_BETWEEN_PAGES` | `0.3s` | Pause between paginated requests |
| `RETRY_DELAYS` | `[5, 15, 30]s` | Wait times between retries on failure |
| `REQUEST_TIMEOUT` | `20s` | Per-request timeout |
