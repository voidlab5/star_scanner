StarBT Installment Finder 🌟💳
A lightweight Python scraper that tracks the maximum number of interest-free installments (rate fără dobândă) available via Banca Transilvania's STAR Card program for your favorite tech, music, and book retailers.

Instead of manually navigating the starbt.ro portal, this script queries the partner database, handles pagination automatically, cleans up doubled partner names, and outputs a clean, sorted text summary.

🚀 Quick Start
1. Install Dependencies
This script relies on requests for fetching network pages and BeautifulSoup4 for parsing the HTML. Install them using pip:

Bash
pip install requests beautifulsoup4
2. Run the Script
Execute the script straight from your terminal:

Bash
python starbt.py
🔧 Customizing the Monitored Stores
The script tracks specific brands using a hardcoded array (list) directly inside the code. To add, remove, or change which stores you are tracking, you need to edit the Python file (starbt.py) in a text editor.

Open starbt.py.

Locate the WATCHED_STORES block near the top of the file:

Python
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
To add a store: Append a new lowercase string inside quotes, ensuring it matches the beginning of the brand's name on the StarBT platform (e.g., "ikea" or "f64"). Don't forget the comma!

To remove a store: Simply delete its line from the list.

Save the file and run it again.

🛠️ Script Architecture & Features
Resilient Fetching: Includes a robust retry mechanism (fetch_with_retry) handling aggressive rate-limiting (HTTP 429 with Retry-After headers) and server drops (HTTP 503).

Deep Pagination Parsing: Intelligently looks for total page counts across standard HTML anchors, dynamic onclick Javascript pagination hooks, and data-page properties.

Strict Name Verification: Employs a custom prefix matcher (_name_matches) to ensure searching for emag doesn't leak false positives like kafemag or ledemag.

Data Sanitization: Detects and fixes doubled string artifacts sometimes produced by layout parsers (e.g., transforming EMAGEEMAG safely back to EMAG).

⚙️ Additional Settings
You can also adjust execution settings right below the store block:

Python
DELAY_BETWEEN_PAGES = 0.3   # Politeness delay between pagination hits (seconds)
RETRY_DELAYS        = [5, 15, 30] # Wait progression if the server rejects a request
REQUEST_TIMEOUT     = 20    # Connection timeout barrier
📋 Sample Output Format
Plaintext
Searching: altex
Searching: carturesti
Searching: emag
...

==================================================
  Watched stores — current installment counts
==================================================

  ALTEX                               12 rate
  Carturesti                          6 rate
  eMAG                                24 rate
  PC GARAGE                           12 rate
  (vexio — not found)
