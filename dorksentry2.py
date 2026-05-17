#!/usr/bin/env python3
"""
DorkSentry v1.0 - Professional Google Dorking Tool
====================================================
Single-file OSINT reconnaissance tool for authorized security research.

Usage Examples:
    python dorksentry.py -q "intext:'bug bounty' inurl:hackerone"
    python dorksentry.py --site example.com --dork "admin login"
    python dorksentry.py --template bug_bounty --count 50
    python dorksentry.py --template jobs_python --extra "senior"
    python dorksentry.py --list-templates
    python dorksentry.py --interactive
    python dorksentry.py -q "exposed .env files" --validate --export json,csv,html
    python dorksentry.py -q "bug bounty" --time-range week

Requirements:
    pip install requests beautifulsoup4

Author: DorkSentry Project
License: MIT (for authorized use only)
"""

# ============================================================================
# SECTION 1: IMPORTS AND METADATA
# ============================================================================

import argparse
import csv
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urlparse, urlencode

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("[INFO]  Install with: pip install requests beautifulsoup4")
    sys.exit(1)

__version__ = "1.0.1"
__author__  = "DorkSentry Project"

# ============================================================================
# SECTION 2: CONSTANTS AND EMBEDDED DATA
# ============================================================================

# ---------- ANSI colour codes ------------------------------------------------
RESET   = '\033[0m'
BOLD    = '\033[1m'
RED     = '\033[91m'
GREEN   = '\033[92m'
YELLOW  = '\033[93m'
BLUE    = '\033[94m'
MAGENTA = '\033[95m'
CYAN    = '\033[96m'
WHITE   = '\033[97m'
DIM     = '\033[2m'

# ---------- ASCII banner ------------------------------------------------------
BANNER = f"""{CYAN}{BOLD}
 ____             _    ____            _              
|  _ \  ___  _ __| | _/ ___|  ___ _ __ | |_ _ __ _   _ 
| | | |/ _ \| '__| |/ /\___ \ / _ \ '_ \| __| '__| | | |
| |_| | (_) | |  |   <  ___) |  __/ | | | |_| |  | |_| |
|____/ \___/|_|  |_|\_\|____/ \___|_| |_|\__|_|   \__, |
                                                    |___/ 
{RESET}{DIM}  v{__version__} — Professional Google Dorking & OSINT Tool{RESET}
{YELLOW}  [ For authorized security research only ]{RESET}
"""

# ---------- Legal disclaimer --------------------------------------------------
DISCLAIMER = f"""
{RED}{BOLD}{'='*65}
                     LEGAL DISCLAIMER
{'='*65}{RESET}
{YELLOW}
DorkSentry is intended ONLY for:
  • Authorized penetration testing of systems you own
  • Security research with explicit written permission
  • Educational and academic purposes
  • Bug bounty hunting within defined program scopes

USE OF THIS TOOL AGAINST SYSTEMS WITHOUT AUTHORIZATION MAY
VIOLATE COMPUTER FRAUD LAWS IN YOUR JURISDICTION.

The author(s) assume NO liability for misuse of this tool.
{RESET}{RED}{BOLD}{'='*65}{RESET}
"""

DISCLAIMER_FILE = Path.home() / ".dorksentry_agreed"

# ---------- User-Agent pool (25 real agents) ----------------------------------
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Vivaldi/6.5.3206.48",
]

# ---------- Time-range mapping ------------------------------------------------
TIME_RANGE_MAP: Dict[str, str] = {
    "day":   "qdr:d",
    "week":  "qdr:w",
    "month": "qdr:m",
    "year":  "qdr:y",
}

# ---------- Dork templates dictionary ----------------------------------------
DORK_TEMPLATES: Dict[str, Dict] = {
    "bug_bounty": {
        "description": "Find bug bounty programs",
        "queries": [
            'intext:"bug bounty" inurl:security',
            'intext:"vulnerability disclosure" inurl:security',
            'intext:"responsible disclosure" inurl:security',
            '"submit vulnerability" "reward"',
        ],
    },
    "jobs_python": {
        "description": "Find Python developer jobs",
        "queries": [
            'intitle:"python developer" (remote OR "work from home")',
            'intext:"hiring python" inurl:careers',
            'site:linkedin.com "python developer" "remote"',
        ],
    },
    "jobs_general": {
        "description": "Find job postings (customizable)",
        "queries": [
            'intitle:"job" OR intitle:"career" OR intitle:"hiring"',
            'intext:"apply now" inurl:jobs',
            'site:greenhouse.io OR site:lever.co',
        ],
    },
    "exposed_docs": {
        "description": "Find exposed documents",
        "queries": [
            'filetype:pdf confidential',
            'filetype:docx "not for distribution"',
            'filetype:xlsx financial OR budget',
        ],
    },
    "login_pages": {
        "description": "Find login and admin panels",
        "queries": [
            'intitle:"login" OR intitle:"admin"',
            'inurl:admin inurl:login',
            'intitle:"Dashboard" inurl:admin',
        ],
    },
    "api_docs": {
        "description": "Find API documentation",
        "queries": [
            'intitle:"api documentation"',
            'inurl:"/api/v1" OR inurl:"/api/v2"',
            'intext:"api key" inurl:docs',
        ],
    },
    "config_files": {
        "description": "Find exposed configuration files",
        "queries": [
            'filetype:env "DB_PASSWORD"',
            'filetype:config intext:"password"',
            'ext:ini "database"',
        ],
    },
    "wordpress": {
        "description": "WordPress-specific vulnerabilities",
        "queries": [
            'inurl:wp-content/uploads',
            'inurl:wp-admin',
            'inurl:xmlrpc.php',
        ],
    },
    "directories": {
        "description": "Open directory listings",
        "queries": [
            'intitle:"index of /" "parent directory"',
            'intitle:"index of" backup',
            'intitle:"index of" database',
        ],
    },
    "databases": {
        "description": "Exposed database files",
        "queries": [
            'filetype:sql "INSERT INTO"',
            'filetype:db',
            'ext:mdb OR ext:sql OR ext:sqlite',
        ],
    },
    "cameras": {
        "description": "Publicly accessible cameras",
        "queries": [
            'intitle:"webcamXP 5"',
            'inurl:view/view.shtml',
            'intitle:"Live View / - AXIS"',
        ],
    },
    "cloud_storage": {
        "description": "Exposed cloud storage",
        "queries": [
            'site:s3.amazonaws.com',
            'site:blob.core.windows.net',
            'site:storage.googleapis.com',
        ],
    },
}

# ============================================================================
# SECTION 3: DATA CLASSES
# ============================================================================

@dataclass
class SearchResult:
    """Represents a single search result returned by Google.

    Attributes:
        url:         Full URL of the result.
        title:       Page title extracted from <h3>.
        description: Snippet / description text.
        domain:      Extracted domain from url.
        query:       The dork query that produced this result.
        valid:       True if the URL was reachable during validation.
        status_code: HTTP status code from validation (0 = not validated).
        timestamp:   ISO-format timestamp of when the result was collected.
    """

    url:         str
    title:       str
    description: str
    domain:      str          = ""
    query:       str          = ""
    valid:       bool         = False
    status_code: int          = 0
    timestamp:   str          = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        """Derive the domain from the url automatically."""
        if self.url and not self.domain:
            try:
                self.domain = urlparse(self.url).netloc
            except Exception:
                self.domain = ""


@dataclass
class Configuration:
    """Centralised runtime configuration derived from CLI arguments.

    Attributes:
        query:        Raw query string (may be None if template is used).
        site:         Domain restriction (site:xxx).
        dork:         Dork keywords appended to site query.
        template:     Name of a pre-built template.
        extra:        Extra keywords appended to template queries.
        count:        Desired total result count.
        max_requests: Hard cap on HTTP requests to Google.
        base_delay:   Minimum seconds between requests.
        max_delay:    Maximum seconds (for exponential back-off).
        time_range:   One of day/week/month/year.
        validate:     Whether to HTTP-validate each result URL.
        proxy:        Single proxy URL string.
        proxy_file:   Path to a file containing one proxy per line.
        export:       Comma-separated list of export formats.
        output_dir:   Directory where exported files are saved.
        interactive:  Whether to enter interactive mode.
        list_templates: Print template list and exit.
        verbose:      Extra-verbose console output.
        timeout:      Requests timeout in seconds.
        debug_html:   Save raw HTML responses to disk for debugging.
    """

    query:          Optional[str]  = None
    site:           Optional[str]  = None
    dork:           Optional[str]  = None
    template:       Optional[str]  = None
    extra:          Optional[str]  = None
    count:          int            = 50
    max_requests:   int            = 100
    base_delay:     float          = 2.5
    max_delay:      float          = 60.0
    time_range:     Optional[str]  = None
    validate:       bool           = False
    proxy:          Optional[str]  = None
    proxy_file:     Optional[str]  = None
    export:         List[str]      = field(default_factory=list)
    output_dir:     str            = "dorksentry_output"
    interactive:    bool           = False
    list_templates: bool           = False
    verbose:        bool           = False
    timeout:        int            = 15
    debug_html:     bool           = False


# ============================================================================
# SECTION 4: UTILITY CLASSES
# ============================================================================

class ColorPrinter:
    """Provides colourised, levelled console output using ANSI escape codes."""

    def __init__(self, verbose: bool = False) -> None:
        """Initialise the printer.

        Args:
            verbose: When True, DEBUG-level messages are printed.
        """
        self.verbose = verbose

    def info(self, msg: str) -> None:
        """Print an informational message in cyan.

        Args:
            msg: The message to display.
        """
        print(f"{CYAN}[INFO]{RESET}  {msg}")

    def success(self, msg: str) -> None:
        """Print a success message in green.

        Args:
            msg: The message to display.
        """
        print(f"{GREEN}[OK]{RESET}    {msg}")

    def warning(self, msg: str) -> None:
        """Print a warning message in yellow.

        Args:
            msg: The message to display.
        """
        print(f"{YELLOW}[WARN]{RESET}  {msg}")

    def error(self, msg: str) -> None:
        """Print an error message in red.

        Args:
            msg: The message to display.
        """
        print(f"{RED}[ERR]{RESET}   {msg}", file=sys.stderr)

    def result(self, index: int, res: "SearchResult") -> None:
        """Print a formatted search result to the console.

        Args:
            index: 1-based result index.
            res:   The SearchResult object to display.
        """
        validity = f"{GREEN}✓{RESET}" if res.valid else f"{DIM}?{RESET}"
        print(
            f"\n  {BOLD}{BLUE}[{index:03d}]{RESET} {validity} {BOLD}{res.title[:80]}{RESET}\n"
            f"       {CYAN}{res.url[:100]}{RESET}\n"
            f"       {DIM}{res.description[:120]}{RESET}"
        )

    def debug(self, msg: str) -> None:
        """Print a debug message if verbose mode is active.

        Args:
            msg: The message to display.
        """
        if self.verbose:
            print(f"{DIM}[DBG]   {msg}{RESET}")

    def banner(self) -> None:
        """Print the ASCII art banner."""
        print(BANNER)

    def section(self, title: str) -> None:
        """Print a formatted section header.

        Args:
            title: Section title text.
        """
        bar = "─" * 60
        print(f"\n{MAGENTA}{bar}{RESET}")
        print(f"{MAGENTA}  {title}{RESET}")
        print(f"{MAGENTA}{bar}{RESET}")


class RateLimiter:
    """Enforces adaptive rate limiting with exponential back-off.

    Starts at *base_delay* seconds, and doubles the wait time
    every time ``backoff()`` is called, capping at *max_delay*.
    ``reset()`` returns to the base delay.
    """

    def __init__(self, base_delay: float = 2.5, max_delay: float = 60.0) -> None:
        """Initialise the rate limiter.

        Args:
            base_delay: Initial / minimum seconds between requests.
            max_delay:  Maximum seconds the limiter will wait.
        """
        self.base_delay    = base_delay
        self.max_delay     = max_delay
        self.current_delay = base_delay

    def wait(self) -> None:
        """Sleep for the current delay, adding a small random jitter.

        Jitter is ±20 % of the current delay to avoid fingerprinting.
        """
        jitter = self.current_delay * random.uniform(-0.2, 0.2)
        sleep_for = max(0.5, self.current_delay + jitter)
        time.sleep(sleep_for)

    def backoff(self) -> None:
        """Double the delay (exponential back-off), capped at max_delay."""
        self.current_delay = min(self.current_delay * 2.0, self.max_delay)

    def reset(self) -> None:
        """Return the delay to the configured base value."""
        self.current_delay = self.base_delay

    @property
    def current(self) -> float:
        """Return the current delay value in seconds.

        Returns:
            Current delay as a float.
        """
        return self.current_delay


class ProxyManager:
    """Manages a pool of HTTP/HTTPS proxies using round-robin selection.

    Supports a single proxy passed as a string **or** a file containing
    one proxy per line (``http://host:port`` format).
    """

    def __init__(
        self,
        proxy: Optional[str] = None,
        proxy_file: Optional[str] = None,
    ) -> None:
        """Initialise the proxy manager.

        Args:
            proxy:      Single proxy string (e.g. ``http://127.0.0.1:8080``).
            proxy_file: Path to a text file with one proxy per line.
        """
        self._proxies: List[str] = []
        self._index:   int       = 0

        if proxy:
            self._proxies.append(proxy.strip())

        if proxy_file:
            loaded = self.load_proxies_from_file(proxy_file)
            self._proxies.extend(loaded)

    def load_proxies_from_file(self, filepath: str) -> List[str]:
        """Read proxies from a text file, one per line.

        Args:
            filepath: Absolute or relative path to the proxy list file.

        Returns:
            List of proxy URL strings.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(
                f"Error: Proxy file not found: {filepath}. "
                "Try: create the file with one proxy per line."
            )
        proxies: List[str] = []
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    proxies.append(stripped)
        return proxies

    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Return the next proxy in the rotation as a requests-compatible dict.

        Returns:
            Dict like ``{'http': 'http://...', 'https': 'http://...'}``
            or ``None`` if no proxies are configured.
        """
        if not self._proxies:
            return None
        proxy_url          = self._proxies[self._index % len(self._proxies)]
        self._index       += 1
        return {"http": proxy_url, "https": proxy_url}

    @property
    def has_proxies(self) -> bool:
        """Return True if at least one proxy is configured.

        Returns:
            Boolean indicating proxy availability.
        """
        return bool(self._proxies)

    @property
    def count(self) -> int:
        """Return the number of proxies in the pool.

        Returns:
            Integer count of proxies.
        """
        return len(self._proxies)


class ResultValidator:
    """Validates whether discovered URLs are actually reachable via HTTP.

    Uses ``requests.head()`` first; falls back to a lightweight ``requests.get()``
    (with ``stream=True``) if the server returns 405 Method Not Allowed.
    """

    def __init__(
        self,
        proxy_manager: ProxyManager,
        timeout:       int = 10,
    ) -> None:
        """Initialise the validator.

        Args:
            proxy_manager: ProxyManager instance for optional proxy use.
            timeout:       Seconds before a validation request times out.
        """
        self.proxy_manager = proxy_manager
        self.timeout       = timeout

    def validate(self, result: "SearchResult") -> "SearchResult":
        """Attempt to reach the URL and populate status_code / valid fields.

        Args:
            result: A SearchResult whose url field will be tested.

        Returns:
            The same SearchResult with valid and status_code updated.
        """
        if not result.url.startswith("http"):
            result.valid       = False
            result.status_code = 0
            return result

        proxies = self.proxy_manager.get_next_proxy()
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
        }

        try:
            resp = requests.head(
                result.url,
                headers=headers,
                proxies=proxies,
                timeout=self.timeout,
                allow_redirects=True,
            )
            result.status_code = resp.status_code
            result.valid       = resp.status_code < 400

            # 405 = HEAD not allowed; retry with GET streaming
            if resp.status_code == 405:
                resp = requests.get(
                    result.url,
                    headers=headers,
                    proxies=proxies,
                    timeout=self.timeout,
                    stream=True,
                )
                result.status_code = resp.status_code
                result.valid       = resp.status_code < 400
                resp.close()

        except requests.Timeout:
            result.valid       = False
            result.status_code = 0
        except requests.RequestException:
            result.valid       = False
            result.status_code = 0

        return result


# ============================================================================
# SECTION 5: CORE SEARCH ENGINE
# ============================================================================

class GoogleSearcher:
    """Performs Google searches via direct HTTP requests and parses the HTML.

    Google's HTML structure changes occasionally.  This implementation tries
    multiple CSS selectors / tag patterns to stay robust against minor layout
    changes.

    Rate-limiting, proxy rotation, and user-agent rotation are handled
    internally.
    """

    # Google search base URL
    _BASE_URL = "https://www.google.com/search"

    # Selectors tried in order to find result containers (UPDATED 2024)
    _CONTAINER_SELECTORS = [
        # Current 2024 selectors (most reliable first)
        "div[data-hveid][data-ved]",    # Most stable attribute combo
        "div.MjjYud",                    # 2024 outer wrapper
        "div.g.Ww4FFb",                  # Variant
        "div.tF2Cxc",                    # Still works sometimes
        "div.Gx5Zad",                    # Legacy
        "div.g",                         # Legacy fallback
        "div[jscontroller]",             # Broad fallback
    ]

    def __init__(
        self,
        config:        Configuration,
        rate_limiter:  RateLimiter,
        proxy_manager: ProxyManager,
        printer:       ColorPrinter,
    ) -> None:
        """Initialise the searcher with shared configuration objects.

        Args:
            config:        Runtime configuration dataclass.
            rate_limiter:  RateLimiter instance for pacing requests.
            proxy_manager: ProxyManager instance for optional proxy rotation.
            printer:       ColorPrinter for colourised console output.
        """
        self.config        = config
        self.rate_limiter  = rate_limiter
        self.proxy_manager = proxy_manager
        self.printer       = printer
        self._request_count = 0
        self._session       = requests.Session()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(self, query: str) -> List[SearchResult]:
        """Execute a Google search for *query* and return all gathered results.

        Paginates until config.count results are collected or the hard cap
        config.max_requests is reached.

        Args:
            query: A complete Google dork query string.

        Returns:
            List of SearchResult objects (may be shorter than count if Google
            returns fewer results).
        """
        results:    List[SearchResult] = []
        seen_urls:  set                = set()
        page        = 0
        per_page    = min(10, self.config.count)   # Google caps at 10 per page

        self.printer.info(f"Searching: {BOLD}{query}{RESET}")

        while len(results) < self.config.count:
            if self._request_count >= self.config.max_requests:
                self.printer.warning(
                    f"Request cap reached ({self.config.max_requests}). Stopping."
                )
                break

            start  = page * per_page
            batch  = self._fetch_page(query, num=per_page, start=start)

            if batch is None:
                # None signals a hard error / CAPTCHA
                self.printer.warning("Stopping pagination due to fetch error.")
                break

            if not batch:
                # Empty page → no more results
                self.printer.debug(f"Empty page at offset {start}. Done.")
                break

            for item in batch:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    item.query = query
                    results.append(item)

            self.printer.debug(
                f"Page {page + 1}: +{len(batch)} results "
                f"({len(results)} total, delay={self.rate_limiter.current:.1f}s)"
            )

            page += 1
            # Respect rate limiting between pages
            if len(results) < self.config.count:
                self.rate_limiter.wait()

        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_url(self, query: str, num: int, start: int) -> str:
        """Construct the Google search URL with query parameters.

        Args:
            query: URL-encoded search query.
            num:   Number of results requested per page.
            start: Pagination offset.

        Returns:
            Full URL string ready for requests.get().
        """
        params: Dict[str, str] = {
            "q":    query,
            "num":  str(num),
            "start": str(start),
            "hl":   "en",
            "gl":   "us",
        }

        if self.config.time_range:
            tbs_value = TIME_RANGE_MAP.get(self.config.time_range)
            if tbs_value:
                params["tbs"] = tbs_value

        return f"{self._BASE_URL}?{urlencode(params)}"

    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP request headers with a random user-agent.

        Returns:
            Dictionary of HTTP headers.
        """
        return {
            "User-Agent":      random.choice(USER_AGENTS),
            "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT":             "1",
            "Connection":      "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest":  "document",
            "Sec-Fetch-Mode":  "navigate",
            "Sec-Fetch-Site":  "none",
            "Cache-Control":   "max-age=0",
        }

    def _fetch_page(
        self,
        query: str,
        num:   int,
        start: int,
    ) -> Optional[List[SearchResult]]:
        """Fetch one page of Google results and parse it into SearchResult objects.

        Returns ``None`` on a hard error (network failure, CAPTCHA detected).
        Returns an empty list when the page contains no results.

        Args:
            query: The dork query string.
            num:   Results to request per page.
            start: Pagination offset.

        Returns:
            List of SearchResult objects, empty list, or None.
        """
        url     = self._build_url(query, num=num, start=start)
        headers = self._build_headers()
        proxies = self.proxy_manager.get_next_proxy()

        self.printer.debug(f"GET {url}")

        try:
            resp = self._session.get(
                url,
                headers = headers,
                proxies = proxies,
                timeout = self.config.timeout,
                allow_redirects = True,
            )
            self._request_count += 1

        except requests.Timeout:
            self.printer.warning(
                f"Request timed out after {self.config.timeout}s. "
                "Try: increase --timeout or check network."
            )
            self.rate_limiter.backoff()
            return None

        except requests.RequestException as exc:
            self.printer.error(
                f"Network error: {exc}. Try: check proxy settings or network."
            )
            self.rate_limiter.backoff()
            return None

        # ---- Check if redirected to /sorry/ or consent page (FIX #3) ----
        if "/sorry/" in resp.url or "consent.google" in resp.url:
            self.printer.warning(
                f"Google redirected to: {resp.url}\n"
                "  → Soft block detected. Increase --delay or use --proxy"
            )
            self.rate_limiter.backoff()
            return None

        # ---- Check for CAPTCHA or rate-limit response --------------------
        if resp.status_code == 429:
            self.printer.warning(
                "Google returned 429 Too Many Requests. Backing off..."
            )
            self.rate_limiter.backoff()
            self.rate_limiter.wait()
            return None

        if resp.status_code != 200:
            self.printer.warning(
                f"Unexpected HTTP {resp.status_code} from Google."
            )
            self.rate_limiter.backoff()
            return None

        # ---- Parse HTML --------------------------------------------------
        return self._parse_results(resp.text, query)

    def _parse_results(self, html: str, query: str) -> List[SearchResult]:
        """Parse Google search result HTML into SearchResult objects.

        Tries multiple CSS selectors because Google's HTML class names change.
        Falls back to a broad <a href> scan if structured selectors fail.

        Args:
            html:  Raw HTML string from Google's response.
            query: The query that produced this HTML (stored on each result).

        Returns:
            List of SearchResult objects extracted from the page.
        """
        
        # ---- FIX #1: Save raw HTML for debugging (ENHANCED) -------------
        if self.config.debug_html:
            debug_path = Path("google_response_debug.html")
            try:
                debug_path.write_text(html, encoding="utf-8")
                self.printer.debug(
                    f"Raw HTML saved to {debug_path} ({len(html)} bytes)"
                )
            except OSError as e:
                self.printer.warning(f"Could not save debug HTML: {e}")
        
        soup    = BeautifulSoup(html, "html.parser")
        results: List[SearchResult] = []

        # ---- CAPTCHA detection (IMPROVED FIX #1) ------------------------
        if self._is_captcha_page(soup):
            self.printer.warning(
                "CAPTCHA/block page detected! Google is blocking requests.\n"
                "  → Try: increase --delay to 10+, use --proxy, or wait before retrying.\n"
                f"  → Use --debug-html to save the response and inspect it in a browser."
            )
            return []

        # ---- Strategy 1: Try known result-container selectors -----------
        containers: list = []
        for selector in self._CONTAINER_SELECTORS:
            containers = soup.select(selector)
            if containers:
                self.printer.debug(
                    f"Selector '{selector}' matched {len(containers)} containers."
                )
                break

        if containers:
            for container in containers:
                result = self._extract_from_container(container, query)
                if result:
                    results.append(result)

        # ---- Strategy 2: Broad anchor-tag fallback ----------------------
        if not results:
            self.printer.debug("Container selectors failed; using anchor fallback.")
            results = self._extract_from_anchors(soup, query)

        # ---- FIX #4: Verbose HTML stats when no results found -----------
        if not results and self.config.verbose:
            title_tag = soup.find("title")
            all_divs  = len(soup.find_all("div"))
            all_links = len(soup.find_all("a"))
            self.printer.debug(
                f"Page title: '{title_tag.text if title_tag else 'NONE'}' | "
                f"divs={all_divs} | links={all_links} | "
                f"html_size={len(html)} bytes"
            )
            self.printer.warning(
                "Zero results parsed. This usually means:\n"
                "  1. Google served a CAPTCHA/consent page (check --debug-html output)\n"
                "  2. CSS selectors are outdated (report this as an issue)\n"
                "  3. Query returned no results on Google itself"
            )

        return results

    def _extract_from_container(
        self,
        container: "BeautifulSoup",
        query: str,
    ) -> Optional[SearchResult]:
        """Extract title, URL, and description from a single result container.

        Args:
            container: A BeautifulSoup Tag representing one search result block.
            query:     The query string to store on the result.

        Returns:
            A SearchResult, or None if essential fields could not be found.
        """
        # Title — always in the first <h3>
        h3  = container.find("h3")
        title = h3.get_text(strip=True) if h3 else ""

        # URL — find <a> with an href starting with http
        url  = ""
        link = container.find("a", href=True)
        if link:
            raw_href = link.get("href", "")
            url      = self._clean_url(raw_href)

        if not url:
            return None

        # Description — Google uses several class names over time
        description = ""
        desc_classes = [
            "VwiC3b", "s3v9rd", "IsZvec", "lEBKkf",
            "yXK7lf", "st", "aCOpRe",
        ]
        for cls in desc_classes:
            desc_el = container.find(class_=cls)
            if desc_el:
                description = desc_el.get_text(separator=" ", strip=True)
                break

        # Broad fallback: just grab paragraph text from container
        if not description:
            paras = container.find_all(["p", "span"])
            description = " ".join(
                p.get_text(strip=True) for p in paras if p.get_text(strip=True)
            )[:250]

        return SearchResult(
            url         = url,
            title       = title or urlparse(url).netloc,
            description = description,
            query       = query,
        )

    def _extract_from_anchors(
        self,
        soup:  "BeautifulSoup",
        query: str,
    ) -> List[SearchResult]:
        """Fallback: extract results by scanning all <a> tags for real URLs.

        Skips Google-internal links, image links, and navigation anchors.

        Args:
            soup:  Parsed BeautifulSoup document.
            query: Query string to associate with found results.

        Returns:
            List of SearchResult objects.
        """
        results:   List[SearchResult] = []
        seen_urls: set                = set()

        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "")
            url  = self._clean_url(href)

            if not url or url in seen_urls:
                continue
            if self._is_google_internal(url):
                continue

            seen_urls.add(url)

            # Nearest h3 or parent text as title
            parent = anchor.find_parent()
            h3     = parent.find("h3") if parent else None
            title  = h3.get_text(strip=True) if h3 else anchor.get_text(strip=True)

            results.append(
                SearchResult(
                    url         = url,
                    title       = title or urlparse(url).netloc,
                    description = "",
                    query       = query,
                )
            )

        return results

    @staticmethod
    def _clean_url(raw: str) -> str:
        """Normalise and validate a raw href string.

        Google wraps real URLs inside ``/url?q=…`` redirects.  This method
        unwraps them and discards Google-internal paths.

        Args:
            raw: The raw href value from an <a> tag.

        Returns:
            A clean URL string, or empty string if not a real result URL.
        """
        if not raw:
            return ""

        # Unwrap Google redirect: /url?q=https://example.com&...
        if raw.startswith("/url?"):
            parsed = urlparse(raw)
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            if "q" in qs:
                raw = qs["q"][0]

        # Must be an http/https URL after unwrapping
        if not raw.startswith("http"):
            return ""

        # Strip Google tracking parameters
        try:
            parsed = urlparse(raw)
            clean  = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            # Remove empty trailing slashes for deduplication consistency
            return clean.rstrip("/") if clean.endswith("/") and parsed.path != "/" else clean
        except Exception:
            return raw

    @staticmethod
    def _is_google_internal(url: str) -> bool:
        """Return True if the URL points to a Google-owned property.

        Args:
            url: URL string to inspect.

        Returns:
            True if the URL should be excluded from results.
        """
        google_domains = (
            "google.com", "google.co.", "googleapis.com",
            "googleadservices.com", "youtube.com", "gstatic.com",
            "accounts.google", "support.google", "policies.google",
        )
        lower = url.lower()
        return any(d in lower for d in google_domains)

    @staticmethod
    def _is_captcha_page(soup: "BeautifulSoup") -> bool:
        """Heuristically detect if Google has served a CAPTCHA/block page.

        Args:
            soup: Parsed BeautifulSoup document.

        Returns:
            True if CAPTCHA indicators are found.
        """
        # IMPROVED FIX #1: Enhanced detection patterns
        indicators = [
            "unusual traffic",
            "captcha",
            "recaptcha",
            "detected unusual traffic from your computer network",
            "verify you are a human",
            # NEW 2024 patterns:
            "before you continue",
            "our systems have detected",
            "sorry/index",
            "consent.google",
            "too many requests",
            "enable javascript",
            "cookies to display",
            "automated queries",
            "terms of service",
        ]
        
        body_text = soup.get_text(separator=" ").lower()
        
        # Check text indicators
        if any(ind in body_text for ind in indicators):
            return True
        
        # FIX #1: Check canonical URL for /sorry/ redirect
        canonical = soup.find("link", rel="canonical")
        if canonical:
            href = str(canonical.get("href", "")).lower()
            if "sorry" in href or "consent" in href:
                return True
        
        # FIX #1: Check if page has suspiciously little content
        # Real search pages have hundreds of words; block pages are minimal
        if len(body_text.strip()) < 500:
            return True
        
        # FIX #1: Check for consent form elements
        if soup.find("form", {"action": re.compile(r"consent|continue")}):
            return True
            
        return False


# ============================================================================
# SECTION 5 (continued): Query builder functions
# ============================================================================

def build_site_query(site: str, dork: str) -> str:
    """Combine a site restriction with dork keywords into a query string.

    Args:
        site: Domain name (e.g. ``example.com``).
        dork: Dork keywords or operators (e.g. ``inurl:admin``).

    Returns:
        A complete Google query string (e.g. ``site:example.com inurl:admin``).
    """
    return f"site:{site} {dork}".strip()


def build_template_queries(
    template_name: str,
    extra:         Optional[str] = None,
    site:          Optional[str] = None,
) -> List[str]:
    """Expand a template into a list of concrete query strings.

    Optionally prepends a ``site:`` restriction and/or appends extra keywords.

    Args:
        template_name: Key in DORK_TEMPLATES (e.g. ``"bug_bounty"``).
        extra:         Optional extra keywords appended to each query.
        site:          Optional domain to restrict with ``site:`` operator.

    Returns:
        List of fully-formed query strings.

    Raises:
        ValueError: If template_name is not found in DORK_TEMPLATES.
    """
    if template_name not in DORK_TEMPLATES:
        raise ValueError(
            f"Error: Unknown template '{template_name}'. "
            f"Try: --list-templates to see available options."
        )

    template = DORK_TEMPLATES[template_name]
    queries: List[str] = []

    for q in template["queries"]:
        parts: List[str] = []
        if site:
            parts.append(f"site:{site}")
        parts.append(q)
        if extra:
            parts.append(extra)
        queries.append(" ".join(parts))

    return queries


# ============================================================================
# SECTION 6: RESULT PROCESSOR
# ============================================================================

class ResultProcessor:
    """Post-processes a list of SearchResult objects: dedup, stats, validation."""

    def __init__(
        self,
        printer:   ColorPrinter,
        validator: Optional[ResultValidator] = None,
    ) -> None:
        """Initialise the processor.

        Args:
            printer:   ColorPrinter for status messages.
            validator: Optional ResultValidator; if None, validation is skipped.
        """
        self.printer   = printer
        self.validator = validator

    def deduplicate(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on URL.

        Args:
            results: Raw list of SearchResult objects (may contain duplicates).

        Returns:
            New list with duplicates removed, preserving insertion order.
        """
        seen: set         = set()
        unique: List[SearchResult] = []
        for r in results:
            if r.url not in seen:
                seen.add(r.url)
                unique.append(r)
        removed = len(results) - len(unique)
        if removed:
            self.printer.info(f"Removed {removed} duplicate URL(s).")
        return unique

    def validate_all(self, results: List[SearchResult]) -> List[SearchResult]:
        """HTTP-validate all results, updating valid and status_code fields.

        Args:
            results: List of SearchResult objects to validate.

        Returns:
            The same list with validation fields updated in-place.
        """
        if not self.validator:
            return results

        total = len(results)
        self.printer.info(f"Validating {total} URLs …")

        for idx, result in enumerate(results, start=1):
            print(
                f"\r  {CYAN}Validating{RESET} {idx}/{total} — "
                f"{result.url[:60]:<60}",
                end="",
                flush=True,
            )
            self.validator.validate(result)
            # Small delay to avoid hammering target servers
            time.sleep(0.3)

        print()  # newline after inline progress
        valid_count = sum(1 for r in results if r.valid)
        self.printer.success(
            f"Validation complete: {valid_count}/{total} reachable."
        )
        return results

    def extract_domains(self, results: List[SearchResult]) -> Dict[str, int]:
        """Count occurrences of each unique domain across all results.

        Args:
            results: List of SearchResult objects.

        Returns:
            Dict mapping domain → count, sorted by count descending.
        """
        domain_counts: Dict[str, int] = {}
        for r in results:
            if r.domain:
                domain_counts[r.domain] = domain_counts.get(r.domain, 0) + 1
        return dict(
            sorted(domain_counts.items(), key=lambda kv: kv[1], reverse=True)
        )

    def generate_stats(
        self,
        results:      List[SearchResult],
        elapsed:      float,
        queries_used: List[str],
    ) -> Dict:
        """Build a statistics dictionary for reporting / export metadata.

        Args:
            results:      Complete deduplicated result list.
            elapsed:      Wall-clock seconds the search took.
            queries_used: List of query strings executed.

        Returns:
            Dict with keys: total, unique_domains, valid, invalid,
            top_domains, queries, elapsed_seconds, timestamp.
        """
        domains     = self.extract_domains(results)
        valid_count = sum(1 for r in results if r.valid)

        return {
            "total":            len(results),
            "unique_domains":   len(domains),
            "valid":            valid_count,
            "invalid":          len(results) - valid_count,
            "top_domains":      dict(list(domains.items())[:10]),
            "queries":          queries_used,
            "elapsed_seconds":  round(elapsed, 2),
            "timestamp":        datetime.utcnow().isoformat(),
        }

    def print_summary(self, stats: Dict) -> None:
        """Print a formatted summary table to the console.

        Args:
            stats: Statistics dict as returned by generate_stats().
        """
        self.printer.section("SUMMARY")
        print(f"  {BOLD}Total results  :{RESET} {GREEN}{stats['total']}{RESET}")
        print(f"  {BOLD}Unique domains :{RESET} {CYAN}{stats['unique_domains']}{RESET}")
        print(f"  {BOLD}Valid URLs     :{RESET} {GREEN}{stats['valid']}{RESET}")
        print(f"  {BOLD}Elapsed        :{RESET} {stats['elapsed_seconds']}s")
        print(f"  {BOLD}Queries run    :{RESET} {len(stats['queries'])}")

        if stats["top_domains"]:
            print(f"\n  {BOLD}Top domains:{RESET}")
            for domain, count in list(stats["top_domains"].items())[:5]:
                print(f"    {CYAN}{domain:<40}{RESET} {count} result(s)")


# ============================================================================
# SECTION 7: EXPORT HANDLERS
# ============================================================================

def _ensure_output_dir(output_dir: str) -> Path:
    """Create the output directory if it does not exist.

    Args:
        output_dir: Directory path string.

    Returns:
        pathlib.Path object pointing to the directory.
    """
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _timestamped_filename(directory: Path, base: str, extension: str) -> Path:
    """Generate a filename with a UTC timestamp suffix.

    Args:
        directory: Parent directory Path.
        base:      Base filename (e.g. ``"dorksentry_results"``).
        extension: File extension without leading dot (e.g. ``"json"``).

    Returns:
        Full Path object for the output file.
    """
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return directory / f"{base}_{ts}.{extension}"


def export_json(
    results:    List[SearchResult],
    stats:      Dict,
    output_dir: str,
    printer:    ColorPrinter,
) -> Path:
    """Export results to a JSON file with metadata and full result objects.

    Args:
        results:    List of SearchResult objects to export.
        stats:      Statistics dict for the metadata section.
        output_dir: Directory where the file will be written.
        printer:    ColorPrinter for status messages.

    Returns:
        Path to the written file.
    """
    out_path = _timestamped_filename(_ensure_output_dir(output_dir), "dorksentry_results", "json")

    payload = {
        "metadata": {
            "query":         stats.get("queries", []),
            "timestamp":     stats.get("timestamp", datetime.utcnow().isoformat()),
            "total_results": stats.get("total", len(results)),
            "unique_domains": stats.get("unique_domains", 0),
            "elapsed_seconds": stats.get("elapsed_seconds", 0),
        },
        "results": [
            {
                "url":         r.url,
                "title":       r.title,
                "description": r.description,
                "domain":      r.domain,
                "query":       r.query,
                "valid":       r.valid,
                "status_code": r.status_code,
                "timestamp":   r.timestamp,
            }
            for r in results
        ],
    }

    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    printer.success(f"JSON export → {out_path}")
    return out_path


def export_csv(
    results:    List[SearchResult],
    output_dir: str,
    printer:    ColorPrinter,
) -> Path:
    """Export results to a CSV file with standard headers.

    Headers: URL, Title, Description, Domain, Query, Valid, StatusCode, Timestamp

    Args:
        results:    List of SearchResult objects to export.
        output_dir: Directory where the file will be written.
        printer:    ColorPrinter for status messages.

    Returns:
        Path to the written file.
    """
    out_path = _timestamped_filename(_ensure_output_dir(output_dir), "dorksentry_results", "csv")

    fieldnames = ["URL", "Title", "Description", "Domain", "Query", "Valid", "StatusCode", "Timestamp"]

    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "URL":         r.url,
                "Title":       r.title,
                "Description": r.description,
                "Domain":      r.domain,
                "Query":       r.query,
                "Valid":       r.valid,
                "StatusCode":  r.status_code,
                "Timestamp":   r.timestamp,
            })

    printer.success(f"CSV export  → {out_path}")
    return out_path


def export_txt(
    results:    List[SearchResult],
    output_dir: str,
    printer:    ColorPrinter,
) -> Path:
    """Export one URL per line to a plain-text file.

    Args:
        results:    List of SearchResult objects to export.
        output_dir: Directory where the file will be written.
        printer:    ColorPrinter for status messages.

    Returns:
        Path to the written file.
    """
    out_path = _timestamped_filename(_ensure_output_dir(output_dir), "dorksentry_results", "txt")

    with out_path.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(r.url + "\n")

    printer.success(f"TXT export  → {out_path}")
    return out_path


def export_html(
    results:    List[SearchResult],
    stats:      Dict,
    output_dir: str,
    printer:    ColorPrinter,
) -> Path:
    """Export results to a self-contained HTML report with CSS styling.

    The report includes:
    - A metadata header with query, timestamp, and counts.
    - A sortable table of results.
    - A click counter column (client-side JavaScript).

    Args:
        results:    List of SearchResult objects to export.
        stats:      Statistics dict for the report header.
        output_dir: Directory where the file will be written.
        printer:    ColorPrinter for status messages.

    Returns:
        Path to the written file.
    """
    out_path = _timestamped_filename(_ensure_output_dir(output_dir), "dorksentry_results", "html")

    # Build rows
    rows_html_parts: List[str] = []
    for idx, r in enumerate(results, start=1):
        valid_badge = (
            '<span style="color:#2ecc71;font-weight:bold;">✓ Live</span>'
            if r.valid else
            '<span style="color:#95a5a6;">? Unknown</span>'
        )
        safe_title = r.title.replace("<", "&lt;").replace(">", "&gt;")
        safe_desc  = r.description.replace("<", "&lt;").replace(">", "&gt;")
        safe_url   = r.url.replace('"', "%22")

        rows_html_parts.append(f"""
        <tr>
            <td style="text-align:center;color:#7f8c8d;">{idx}</td>
            <td>
                <a href="{safe_url}" target="_blank"
                   onclick="countClick(this)"
                   style="color:#3498db;text-decoration:none;font-weight:500;">
                   {safe_title[:80]}
                </a><br>
                <small style="color:#7f8c8d;">{safe_url[:100]}</small><br>
                <small style="color:#95a5a6;">{safe_desc[:160]}</small>
            </td>
            <td style="text-align:center;color:#7f8c8d;">{r.domain}</td>
            <td style="text-align:center;">{valid_badge}</td>
            <td style="text-align:center;color:#e67e22;">{r.status_code or "—"}</td>
            <td style="text-align:center;" id="clicks-{idx}">0</td>
        </tr>""")

    rows_html = "\n".join(rows_html_parts)

    queries_display = "<br>".join(
        q.replace("<", "&lt;").replace(">", "&gt;")
        for q in stats.get("queries", [])
    )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DorkSentry Report — {stats.get('timestamp','')}</title>
<style>
  * {{ box-sizing: border-box; margin:0; padding:0; }}
  body {{ font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;
          background:#0d1117; color:#c9d1d9; line-height:1.6; }}
  header {{ background:linear-gradient(135deg,#1f2937,#111827);
            padding:30px 40px; border-bottom:2px solid #21d4fd; }}
  header h1 {{ font-size:2rem; color:#21d4fd; letter-spacing:2px; }}
  header p  {{ color:#8b949e; margin-top:5px; }}
  .meta-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
                gap:15px; padding:20px 40px; background:#161b22; }}
  .meta-card {{ background:#1c2128; border:1px solid #30363d; border-radius:8px;
                padding:15px; text-align:center; }}
  .meta-card .value {{ font-size:1.8rem; color:#21d4fd; font-weight:bold; }}
  .meta-card .label {{ font-size:0.8rem; color:#8b949e; text-transform:uppercase; }}
  .queries {{ padding:15px 40px; background:#0d1117; font-family:monospace;
              font-size:0.85rem; color:#8b949e; border-bottom:1px solid #21363d; }}
  .container {{ padding:20px 40px; }}
  table {{ width:100%; border-collapse:collapse; }}
  th {{ background:#1c2128; color:#21d4fd; padding:10px 12px;
        text-align:left; border-bottom:2px solid #21d4fd;
        font-size:0.85rem; text-transform:uppercase; letter-spacing:1px; }}
  td {{ padding:10px 12px; border-bottom:1px solid #21272e;
        vertical-align:top; font-size:0.88rem; }}
  tr:hover td {{ background:#1c2128; }}
  footer {{ text-align:center; padding:20px; color:#30363d;
            font-size:0.8rem; border-top:1px solid #21272e; margin-top:20px; }}
</style>
</head>
<body>
<header>
  <h1>🔍 DorkSentry Report</h1>
  <p>Generated: {stats.get('timestamp','')} UTC</p>
</header>

<div class="meta-grid">
  <div class="meta-card"><div class="value">{stats.get('total',0)}</div><div class="label">Results</div></div>
  <div class="meta-card"><div class="value">{stats.get('unique_domains',0)}</div><div class="label">Domains</div></div>
  <div class="meta-card"><div class="value">{stats.get('valid',0)}</div><div class="label">Valid</div></div>
  <div class="meta-card"><div class="value">{stats.get('elapsed_seconds',0)}s</div><div class="label">Elapsed</div></div>
  <div class="meta-card"><div class="value">{len(stats.get('queries',[]))}</div><div class="label">Queries</div></div>
</div>

<div class="queries">
  <strong style="color:#58a6ff;">Queries used:</strong><br>{queries_display}
</div>

<div class="container">
  <table>
    <thead>
      <tr>
        <th style="width:40px;">#</th>
        <th>Title / URL / Description</th>
        <th style="width:180px;">Domain</th>
        <th style="width:90px;">Status</th>
        <th style="width:70px;">HTTP</th>
        <th style="width:70px;">Clicks</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</div>

<footer>DorkSentry v{__version__} — For authorized security research only.</footer>

<script>
function countClick(el) {{
  var row   = el.closest('tr');
  var cells = row.querySelectorAll('td');
  var last  = cells[cells.length - 1];
  last.textContent = parseInt(last.textContent || '0') + 1;
}}
</script>
</body>
</html>"""

    with out_path.open("w", encoding="utf-8") as fh:
        fh.write(html_content)

    printer.success(f"HTML export → {out_path}")
    return out_path


def dispatch_exports(
    formats:    List[str],
    results:    List[SearchResult],
    stats:      Dict,
    output_dir: str,
    printer:    ColorPrinter,
) -> None:
    """Route export requests to the appropriate handler functions.

    Args:
        formats:    List of format strings (e.g. ``["json", "csv", "html"]``).
        results:    Deduplicated SearchResult list.
        stats:      Statistics dict.
        output_dir: Output directory path string.
        printer:    ColorPrinter for feedback.
    """
    handler_map = {
        "json": lambda: export_json(results, stats, output_dir, printer),
        "csv":  lambda: export_csv(results, output_dir, printer),
        "txt":  lambda: export_txt(results, output_dir, printer),
        "html": lambda: export_html(results, stats, output_dir, printer),
    }

    for fmt in formats:
        fmt_lower = fmt.strip().lower()
        if fmt_lower in handler_map:
            try:
                handler_map[fmt_lower]()
            except OSError as exc:
                printer.error(
                    f"Could not write {fmt_lower} export: {exc}. "
                    "Try: check write permissions on output directory."
                )
        else:
            printer.warning(
                f"Unknown export format '{fmt_lower}'. "
                "Valid options: json, csv, txt, html"
            )


# ============================================================================
# SECTION 8: INTERACTIVE MODE
# ============================================================================

def interactive_mode(printer: ColorPrinter) -> Configuration:
    """Run a text-based interactive menu to build a Configuration.

    Guides the user through selecting a mode, query/template, and optional
    features.  Returns a populated Configuration ready for execution.

    Args:
        printer: ColorPrinter for colourised prompts.

    Returns:
        A fully-populated Configuration dataclass.
    """
    printer.section("Interactive Dork Builder")

    cfg = Configuration()

    # ---- Mode selection -------------------------------------------------
    print(f"\n  {BOLD}Select search mode:{RESET}")
    print(f"  {CYAN}1{RESET}. Custom query / dork")
    print(f"  {CYAN}2{RESET}. Template-based search")
    print(f"  {CYAN}3{RESET}. Site-specific search")

    mode_choice = _prompt("Enter choice [1/2/3]", default="1", valid=["1", "2", "3"])

    if mode_choice == "1":
        # Custom query
        cfg.query = _prompt("Enter Google dork query", required=True)

    elif mode_choice == "2":
        # Template
        print(f"\n  {BOLD}Available templates:{RESET}")
        for idx, (name, tmpl) in enumerate(DORK_TEMPLATES.items(), start=1):
            print(f"  {CYAN}{idx:>2}.{RESET} {name:<20} — {DIM}{tmpl['description']}{RESET}")

        template_names = list(DORK_TEMPLATES.keys())
        raw = _prompt("Enter template name or number", required=True)

        # Accept numeric input
        if raw.isdigit():
            tidx = int(raw) - 1
            if 0 <= tidx < len(template_names):
                cfg.template = template_names[tidx]
            else:
                print(f"{RED}Invalid number. Defaulting to 'bug_bounty'.{RESET}")
                cfg.template = "bug_bounty"
        elif raw in DORK_TEMPLATES:
            cfg.template = raw
        else:
            print(f"{RED}Unknown template. Defaulting to 'bug_bounty'.{RESET}")
            cfg.template = "bug_bounty"

        extra_input = _prompt("Extra keywords to append (leave blank to skip)")
        if extra_input:
            cfg.extra = extra_input

    elif mode_choice == "3":
        # Site-specific
        cfg.site = _prompt("Enter target domain (e.g. example.com)", required=True)
        cfg.dork = _prompt("Enter dork/keywords (e.g. inurl:admin)", required=True)

    # ---- Common options -------------------------------------------------
    count_raw = _prompt("How many results to collect? [default: 30]", default="30")
    try:
        cfg.count = max(1, int(count_raw))
    except ValueError:
        cfg.count = 30

    time_choice = _prompt(
        "Time filter? [none/day/week/month/year]",
        default="none",
        valid=["none", "day", "week", "month", "year"],
    )
    if time_choice != "none":
        cfg.time_range = time_choice

    validate_choice = _prompt("Validate URLs with HTTP check? [y/N]", default="n", valid=["y", "n"])
    cfg.validate = validate_choice.lower() == "y"

    export_raw = _prompt(
        "Export formats (comma-separated: json,csv,txt,html) [blank = none]"
    )
    if export_raw.strip():
        cfg.export = [e.strip() for e in export_raw.split(",") if e.strip()]

    proxy_raw = _prompt("Proxy URL (e.g. http://127.0.0.1:8080) [blank = none]")
    if proxy_raw.strip():
        cfg.proxy = proxy_raw.strip()

    delay_raw = _prompt("Min delay between requests in seconds [default: 2.5]", default="2.5")
    try:
        cfg.base_delay = float(delay_raw)
    except ValueError:
        cfg.base_delay = 2.5

    debug_choice = _prompt("Save raw HTML responses for debugging? [y/N]", default="n", valid=["y", "n"])
    cfg.debug_html = debug_choice.lower() == "y"

    print()
    printer.info("Configuration built. Starting search…")
    return cfg


def _prompt(
    message:    str,
    default:    str                = "",
    required:   bool               = False,
    valid:      Optional[List[str]] = None,
) -> str:
    """Display an interactive prompt and return user input.

    Loops until a valid (optionally required) value is provided.

    Args:
        message:  The prompt text displayed to the user.
        default:  Value returned when the user presses Enter with no input.
        required: If True, empty input is not accepted.
        valid:    Optional list of acceptable values (case-insensitive).

    Returns:
        The user's input string, stripped of leading/trailing whitespace.
    """
    while True:
        suffix = f" [{default}]" if default and not required else ""
        raw    = input(f"  {CYAN}?{RESET} {message}{suffix}: ").strip()

        if not raw and default:
            return default

        if not raw and required:
            print(f"  {RED}This field is required.{RESET}")
            continue

        if valid and raw.lower() not in [v.lower() for v in valid]:
            print(f"  {RED}Please enter one of: {', '.join(valid)}{RESET}")
            continue

        return raw


# ============================================================================
# SECTION 8 (continued): Template / disclaimer helpers
# ============================================================================

def list_templates(printer: ColorPrinter) -> None:
    """Print all available dork templates to the console and exit.

    Args:
        printer: ColorPrinter for colourised output.
    """
    printer.section("Available Dork Templates")
    for name, tmpl in DORK_TEMPLATES.items():
        print(f"\n  {BOLD}{CYAN}{name}{RESET}")
        print(f"    {DIM}{tmpl['description']}{RESET}")
        print(f"    {YELLOW}Queries ({len(tmpl['queries'])}):{RESET}")
        for q in tmpl["queries"]:
            print(f"      • {q}")


def show_disclaimer_and_confirm(printer: ColorPrinter) -> None:
    """Display the legal disclaimer and require user acceptance.

    If ``~/.dorksentry_agreed`` already exists, the disclaimer is skipped.
    On first run, the user must type ``agree`` to continue.  Saves the
    acceptance marker file so subsequent runs skip the prompt.

    Args:
        printer: ColorPrinter for colourised output.
    """
    if DISCLAIMER_FILE.exists():
        return  # Already agreed previously

    print(DISCLAIMER)
    response = input(
        f"  {YELLOW}Type {BOLD}'agree'{RESET}{YELLOW} to accept and continue, or press Ctrl+C to exit:{RESET} "
    ).strip().lower()

    if response != "agree":
        printer.error("You must accept the disclaimer to use DorkSentry. Exiting.")
        sys.exit(1)

    try:
        DISCLAIMER_FILE.write_text(
            f"Agreed on {datetime.utcnow().isoformat()} UTC\n",
            encoding="utf-8",
        )
        printer.success("Disclaimer accepted. Agreement saved to ~/.dorksentry_agreed")
    except OSError:
        printer.warning("Could not save agreement file (non-fatal).")


# ============================================================================
# SECTION 9: CLI ARGUMENT PARSER
# ============================================================================

def build_argument_parser() -> argparse.ArgumentParser:
    """Build and return the ArgumentParser for DorkSentry.

    Returns:
        Configured argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog        = "dorksentry",
        description = f"{BOLD}DorkSentry v{__version__}{RESET} — Professional Google Dorking Tool",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = f"""
{BOLD}Examples:{RESET}
  # General dork query
  python dorksentry.py -q "intext:'bug bounty' inurl:hackerone"

  # Site-specific search
  python dorksentry.py --site example.com --dork "inurl:admin"

  # Template search with extra keywords
  python dorksentry.py --template bug_bounty --count 100
  python dorksentry.py --template jobs_python --extra "senior"

  # With validation and exports
  python dorksentry.py -q "filetype:env DB_PASSWORD" --validate --export json,csv,html

  # Time-filtered search
  python dorksentry.py -q "python remote jobs" --time-range week

  # Debug mode (save raw HTML)
  python dorksentry.py -q "site:hackerone.com" --debug-html -v

  # Interactive mode
  python dorksentry.py --interactive

  # List templates
  python dorksentry.py --list-templates
        """,
    )

    # ---- Search modes ---------------------------------------------------
    search_group = parser.add_argument_group("Search modes")
    search_group.add_argument(
        "-q", "--query",
        metavar="QUERY",
        help="Google dork query string (e.g. \"inurl:admin intitle:login\")",
    )
    search_group.add_argument(
        "--site",
        metavar="DOMAIN",
        help="Restrict results to a specific domain (adds site: operator)",
    )
    search_group.add_argument(
        "--dork",
        metavar="DORK",
        help="Dork keywords to combine with --site",
    )
    search_group.add_argument(
        "--template",
        metavar="NAME",
        choices=list(DORK_TEMPLATES.keys()),
        help="Use a pre-built dork template (see --list-templates)",
    )
    search_group.add_argument(
        "--extra",
        metavar="KEYWORDS",
        help="Extra keywords appended to each template query",
    )
    search_group.add_argument(
        "--list-templates",
        action="store_true",
        help="Display all available templates and exit",
    )
    search_group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Launch the interactive dork builder",
    )

    # ---- Search options -------------------------------------------------
    opts_group = parser.add_argument_group("Search options")
    opts_group.add_argument(
        "--count",
        type    = int,
        default = 50,
        metavar = "N",
        help    = "Target number of results to collect (default: 50)",
    )
    opts_group.add_argument(
        "--max-requests",
        type    = int,
        default = 100,
        metavar = "N",
        help    = "Hard cap on Google HTTP requests (default: 100)",
    )
    opts_group.add_argument(
        "--time-range",
        choices = list(TIME_RANGE_MAP.keys()),
        metavar = "RANGE",
        help    = "Filter results by time: day, week, month, year",
    )
    opts_group.add_argument(
        "--validate",
        action = "store_true",
        help   = "HTTP-validate each result URL (slower but verifies reachability)",
    )
    opts_group.add_argument(
        "--timeout",
        type    = int,
        default = 15,
        metavar = "SECS",
        help    = "Request timeout in seconds (default: 15)",
    )

    # ---- Rate limiting --------------------------------------------------
    rate_group = parser.add_argument_group("Rate limiting")
    rate_group.add_argument(
        "--delay",
        type    = float,
        default = 2.5,
        metavar = "SECS",
        help    = "Minimum delay between requests in seconds (default: 2.5)",
    )
    rate_group.add_argument(
        "--max-delay",
        type    = float,
        default = 60.0,
        metavar = "SECS",
        help    = "Maximum back-off delay in seconds (default: 60)",
    )

    # ---- Proxy settings -------------------------------------------------
    proxy_group = parser.add_argument_group("Proxy settings")
    proxy_group.add_argument(
        "--proxy",
        metavar = "URL",
        help    = "Single proxy URL (e.g. http://127.0.0.1:8080)",
    )
    proxy_group.add_argument(
        "--proxy-file",
        metavar = "PATH",
        help    = "File containing one proxy per line for rotation",
    )

    # ---- Output ---------------------------------------------------------
    output_group = parser.add_argument_group("Output / export")
    output_group.add_argument(
        "--export",
        metavar = "FORMATS",
        help    = "Comma-separated export formats: json, csv, txt, html",
    )
    output_group.add_argument(
        "--output-dir",
        metavar = "DIR",
        default = "dorksentry_output",
        help    = "Directory for exported files (default: dorksentry_output)",
    )
    output_group.add_argument(
        "-v", "--verbose",
        action = "store_true",
        help   = "Enable verbose / debug output",
    )
    output_group.add_argument(
        "--debug-html",
        action = "store_true",
        help   = "Save raw HTML responses to google_response_debug.html for troubleshooting",
    )

    return parser


def args_to_config(args: argparse.Namespace) -> Configuration:
    """Convert parsed argparse Namespace into a Configuration dataclass.

    Args:
        args: Populated Namespace from ArgumentParser.parse_args().

    Returns:
        Configuration dataclass ready for use.
    """
    export_formats: List[str] = []
    if args.export:
        export_formats = [e.strip() for e in args.export.split(",") if e.strip()]

    return Configuration(
        query          = args.query,
        site           = args.site,
        dork           = args.dork,
        template       = args.template,
        extra          = getattr(args, "extra", None),
        count          = args.count,
        max_requests   = args.max_requests,
        base_delay     = args.delay,
        max_delay      = args.max_delay,
        time_range     = args.time_range,
        validate       = args.validate,
        proxy          = args.proxy,
        proxy_file     = getattr(args, "proxy_file", None),
        export         = export_formats,
        output_dir     = args.output_dir,
        interactive    = args.interactive,
        list_templates = args.list_templates,
        verbose        = args.verbose,
        timeout        = args.timeout,
        debug_html     = args.debug_html,
    )


# ============================================================================
# SECTION 10: MAIN EXECUTION
# ============================================================================

def resolve_queries(cfg: Configuration, printer: ColorPrinter) -> List[str]:
    """Derive the final list of query strings from a Configuration.

    Handles all three modes: direct query, site+dork, and template.

    Args:
        cfg:     Runtime Configuration.
        printer: ColorPrinter for warnings.

    Returns:
        Non-empty list of query strings.

    Raises:
        ValueError: If the configuration does not specify any search mode.
    """
    queries: List[str] = []

    if cfg.query:
        queries.append(cfg.query)

    if cfg.site and cfg.dork:
        queries.append(build_site_query(cfg.site, cfg.dork))
    elif cfg.site and not cfg.dork:
        printer.warning("--site provided without --dork; searching bare site:")
        queries.append(f"site:{cfg.site}")

    if cfg.template:
        try:
            tqs = build_template_queries(cfg.template, extra=cfg.extra, site=cfg.site)
            queries.extend(tqs)
        except ValueError as exc:
            printer.error(str(exc))

    if not queries:
        raise ValueError(
            "Error: No search mode specified. "
            "Try: -q QUERY, --site DOMAIN --dork DORK, or --template NAME"
        )

    return queries


def run_searches(
    queries:   List[str],
    cfg:       Configuration,
    searcher:  GoogleSearcher,
    printer:   ColorPrinter,
) -> Tuple[List[SearchResult], List[str]]:
    """Execute all queries and collect results.

    Args:
        queries:  List of resolved query strings.
        cfg:      Runtime Configuration.
        searcher: Initialised GoogleSearcher instance.
        printer:  ColorPrinter for feedback.

    Returns:
        Tuple of (all_results, executed_queries).
    """
    all_results:       List[SearchResult] = []
    executed_queries:  List[str]          = []

    for q_idx, query in enumerate(queries, start=1):
        printer.info(
            f"Query {q_idx}/{len(queries)}: {BOLD}{query[:80]}{RESET}"
            + ("…" if len(query) > 80 else "")
        )
        try:
            batch = searcher.search(query)
            all_results.extend(batch)
            executed_queries.append(query)

            printer.success(f"  → {len(batch)} result(s) collected.")

            # Progress counter
            print(
                f"  {DIM}Total so far: {len(all_results)} result(s){RESET}"
            )

            # Delay between distinct queries
            if q_idx < len(queries):
                searcher.rate_limiter.wait()

        except KeyboardInterrupt:
            printer.warning("Search interrupted by user (Ctrl+C).")
            break

    return all_results, executed_queries


def main() -> None:
    """Entry point: parse arguments, run searches, process and export results."""

    # ---- Argument parsing -----------------------------------------------
    parser = build_argument_parser()
    args   = parser.parse_args()

    # ---- Printer (needed before anything else) -------------------------
    printer = ColorPrinter(verbose=getattr(args, "verbose", False))
    printer.banner()

    # ---- Disclaimer -----------------------------------------------------
    show_disclaimer_and_confirm(printer)

    # ---- Build configuration -------------------------------------------
    if args.interactive:
        cfg = interactive_mode(printer)
    else:
        cfg = args_to_config(args)

    # ---- List templates mode -------------------------------------------
    if cfg.list_templates:
        list_templates(printer)
        sys.exit(0)

    # ---- Validate that we have something to search ---------------------
    try:
        queries = resolve_queries(cfg, printer)
    except ValueError as exc:
        printer.error(str(exc))
        parser.print_help()
        sys.exit(1)

    # ---- Warn if aggressive settings are used --------------------------
    if cfg.base_delay < 1.0:
        printer.warning(
            f"Delay of {cfg.base_delay}s is aggressive. "
            "Google may block requests quickly. Recommended: ≥2.5s"
        )
    if cfg.count > 200:
        printer.warning(
            f"Requesting {cfg.count} results may trigger CAPTCHAs. "
            "Consider batching or using proxies."
        )

    # ---- Initialise shared components ----------------------------------
    rate_limiter = RateLimiter(
        base_delay = cfg.base_delay,
        max_delay  = cfg.max_delay,
    )

    try:
        proxy_manager = ProxyManager(
            proxy      = cfg.proxy,
            proxy_file = cfg.proxy_file,
        )
    except FileNotFoundError as exc:
        printer.error(str(exc))
        sys.exit(1)

    if proxy_manager.has_proxies:
        printer.info(f"Proxy pool: {proxy_manager.count} proxy/proxies loaded.")

    validator = ResultValidator(proxy_manager, timeout=cfg.timeout) if cfg.validate else None
    processor = ResultProcessor(printer, validator)
    searcher  = GoogleSearcher(cfg, rate_limiter, proxy_manager, printer)

    # ---- Execute searches ----------------------------------------------
    start_time = time.time()

    printer.section(f"Starting Search  [{len(queries)} query/queries]")

    try:
        all_results, executed_queries = run_searches(queries, cfg, searcher, printer)
    except KeyboardInterrupt:
        printer.warning("Interrupted before any results. Exiting.")
        sys.exit(0)

    elapsed = time.time() - start_time

    # ---- Post-process --------------------------------------------------
    if not all_results:
        printer.warning(
            "No results collected. Possible reasons:\n"
            "  • Google returned a CAPTCHA (try adding a delay or proxy)\n"
            "  • Query returned zero results\n"
            "  • Network connectivity issue\n"
            f"  • Use --debug-html and --verbose to inspect raw responses"
        )
        sys.exit(0)

    # Deduplication
    unique_results = processor.deduplicate(all_results)

    # Validation (optional)
    if cfg.validate:
        unique_results = processor.validate_all(unique_results)

    # ---- Print results -------------------------------------------------
    printer.section(f"Results  ({len(unique_results)} unique)")
    for idx, result in enumerate(unique_results, start=1):
        printer.result(idx, result)
        if idx % 10 == 0:
            print(f"\n  {DIM}--- Showing {idx}/{len(unique_results)} results ---{RESET}\n")

    # ---- Statistics ----------------------------------------------------
    stats = processor.generate_stats(unique_results, elapsed, executed_queries)
    processor.print_summary(stats)

    # ---- Exports -------------------------------------------------------
    if cfg.export:
        printer.section("Exporting Results")
        dispatch_exports(
            formats    = cfg.export,
            results    = unique_results,
            stats      = stats,
            output_dir = cfg.output_dir,
            printer    = printer,
        )

    print(f"\n{GREEN}{BOLD}Done.{RESET}  {DIM}DorkSentry finished in {elapsed:.2f}s.{RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}[WARN]{RESET}  Interrupted by user. Goodbye.\n")
        sys.exit(0)
