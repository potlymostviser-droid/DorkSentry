```markdown
# 🔍 DorkSentry v1.0.1

**Professional Google Dorking & OSINT Reconnaissance Tool**

DorkSentry is a powerful, single-file Python tool for automated Google dorking, OSINT reconnaissance, and security research. It features adaptive rate limiting, proxy support, result validation, and multiple export formats — all wrapped in a beautiful command-line interface.

---

## 📋 Table of Contents

- [Features](#-features)
- [Legal Disclaimer](#️-legal-disclaimer)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
  - [Basic Searches](#basic-searches)
  - [Template-Based Searches](#template-based-searches)
  - [Site-Specific Searches](#site-specific-searches)
  - [Advanced Options](#advanced-options)
  - [Interactive Mode](#interactive-mode)
- [Command-Line Reference](#-command-line-reference)
- [Dork Templates](#-dork-templates)
- [Export Formats](#-export-formats)
- [Troubleshooting](#-troubleshooting)
- [Best Practices](#-best-practices)
- [Examples](#-examples)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Capabilities
- 🎯 **Custom Google Dork Queries** — Execute any Google search operator combination
- 📚 **12 Pre-Built Templates** — Ready-to-use queries for common OSINT tasks
- 🌐 **Site-Specific Searches** — Target individual domains with custom dorks
- 🔄 **Smart Pagination** — Automatic multi-page result collection
- ✅ **HTTP Validation** — Verify URL reachability with configurable timeout
- 📊 **Multiple Export Formats** — JSON, CSV, TXT, and styled HTML reports

### Advanced Features
- 🚦 **Adaptive Rate Limiting** — Exponential backoff prevents Google CAPTCHA
- 🎭 **User-Agent Rotation** — 25 real browser signatures for stealth
- 🌍 **Proxy Support** — Single proxy or rotating pool from file
- ⏱️ **Time-Range Filtering** — Limit results to day/week/month/year
- 🐛 **Debug Mode** — Save raw HTML responses for troubleshooting
- 🎨 **Beautiful CLI** — Color-coded ANSI output with progress indicators
- 💾 **Session Management** — Persistent disclaimer acceptance
- 🤖 **Interactive Mode** — Guided menu for building complex searches

### Technical Highlights
- **Zero dependencies** except `requests` and `beautifulsoup4`
- **Single-file design** — Easy deployment and auditing
- **2024-updated selectors** — Works with current Google HTML structure
- **Enhanced CAPTCHA detection** — 15+ detection patterns
- **Robust error handling** — Clear, actionable error messages

---

## ⚖️ Legal Disclaimer

```
┌─────────────────────────────────────────────────────────────────┐
│                        LEGAL DISCLAIMER                         │
└─────────────────────────────────────────────────────────────────┘

DorkSentry is intended ONLY for:
  • Authorized penetration testing of systems you own
  • Security research with explicit written permission
  • Educational and academic purposes
  • Bug bounty hunting within defined program scopes

USE OF THIS TOOL AGAINST SYSTEMS WITHOUT AUTHORIZATION MAY
VIOLATE COMPUTER FRAUD AND ABUSE LAWS IN YOUR JURISDICTION.

The author(s) assume NO liability for misuse of this tool.
By using DorkSentry, you agree to use it responsibly and legally.
```

**You will be prompted to accept this disclaimer on first run.**

---

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
# Clone or download dorksentry.py
wget https://example.com/dorksentry.py
# or
curl -O https://example.com/dorksentry.py

# Install required packages
pip install requests beautifulsoup4

# Make executable (optional)
chmod +x dorksentry.py
```

### Verify Installation

```bash
python dorksentry.py --help
```

You should see the ASCII banner and help text.

---

## 🚀 Quick Start

### 1. Simple Query Search
```bash
python dorksentry.py -q "intext:'bug bounty' site:hackerone.com"
```

### 2. Use a Template
```bash
python dorksentry.py --template bug_bounty --count 50
```

### 3. Interactive Mode (Recommended for Beginners)
```bash
python dorksentry.py --interactive
```

### 4. With Exports
```bash
python dorksentry.py -q "filetype:pdf confidential" \
    --export json,html \
    --count 100
```

---

## 📖 Usage Guide

### Basic Searches

#### Direct Query
Run any Google dork query:

```bash
python dorksentry.py -q 'intitle:"index of" password'
```

**Common operators:**
- `site:` — Restrict to domain
- `intitle:` — Search page titles
- `inurl:` — Search URLs
- `intext:` — Search page content
- `filetype:` — Find specific file types
- `ext:` — Alternative to filetype
- `"exact phrase"` — Match exact text
- `OR` — Logical OR
- `-exclude` — Exclude terms

#### With Result Count
```bash
python dorksentry.py -q "site:gov filetype:xls" --count 200
```

#### With Time Filter
```bash
python dorksentry.py -q "python remote jobs" --time-range week
```

---

### Template-Based Searches

DorkSentry includes 12 pre-built templates for common tasks.

#### List Available Templates
```bash
python dorksentry.py --list-templates
```

**Output:**
```
Available Dork Templates
────────────────────────────────────────────────────────────

  bug_bounty
    Find bug bounty programs
    Queries (4):
      • intext:"bug bounty" inurl:security
      • intext:"vulnerability disclosure" inurl:security
      • intext:"responsible disclosure" inurl:security
      • "submit vulnerability" "reward"

  exposed_docs
    Find exposed documents
    Queries (3):
      • filetype:pdf confidential
      • filetype:docx "not for distribution"
      • filetype:xlsx financial OR budget

  [... more templates ...]
```

#### Use a Template
```bash
python dorksentry.py --template exposed_docs --count 100
```

#### Template with Extra Keywords
```bash
python dorksentry.py --template jobs_python --extra "senior remote"
```

This appends "senior remote" to each template query.

#### Template with Site Restriction
```bash
python dorksentry.py --template login_pages --site example.com
```

---

### Site-Specific Searches

Target a specific domain with custom dorks:

```bash
python dorksentry.py --site example.com --dork "inurl:admin OR inurl:login"
```

**Equivalent to:**
```
site:example.com inurl:admin OR inurl:login
```

---

### Advanced Options

#### Rate Limiting & Stealth

**Increase delay to avoid CAPTCHA:**
```bash
python dorksentry.py -q "sensitive query" \
    --delay 10 \
    --max-delay 60
```

- `--delay` — Minimum seconds between requests (default: 2.5)
- `--max-delay` — Maximum backoff delay (default: 60)

**With exponential backoff:**
- First request: 10s delay
- If blocked: 20s delay
- If blocked again: 40s delay
- Caps at 60s

#### Proxy Support

**Single proxy:**
```bash
python dorksentry.py -q "query" \
    --proxy "http://127.0.0.1:8080"
```

**Rotating proxy pool:**
```bash
# Create proxies.txt:
# http://proxy1.example.com:8080
# http://proxy2.example.com:8080
# socks5://127.0.0.1:9050

python dorksentry.py -q "query" \
    --proxy-file proxies.txt
```

DorkSentry will round-robin through proxies.

#### Result Validation

Verify that URLs are actually reachable:

```bash
python dorksentry.py -q "query" --validate
```

- Uses `HEAD` request first (fast)
- Falls back to `GET` if server returns 405
- Updates `status_code` and `valid` fields
- Adds ~0.3s delay per URL to avoid overwhelming targets

#### Export Formats

```bash
python dorksentry.py -q "query" \
    --export json,csv,html,txt \
    --output-dir my_results
```

**Formats:**
- `json` — Structured data with metadata
- `csv` — Spreadsheet-compatible
- `txt` — Plain URL list (one per line)
- `html` — Beautiful interactive report

#### Verbose & Debug Mode

**Verbose output:**
```bash
python dorksentry.py -q "query" --verbose
```

Shows:
- CSS selector match details
- Pagination debug info
- HTML statistics when parsing fails

**Debug HTML dump:**
```bash
python dorksentry.py -q "query" --debug-html --verbose
```

Saves raw Google response to `google_response_debug.html` — open in browser to see exactly what Google returned (useful for diagnosing CAPTCHAs).

---

### Interactive Mode

Perfect for beginners or complex multi-step workflows:

```bash
python dorksentry.py --interactive
```

**Walkthrough:**
```
Interactive Dork Builder
────────────────────────────────────────────────────────────

  Select search mode:
  1. Custom query / dork
  2. Template-based search
  3. Site-specific search

  ? Enter choice [1/2/3] [1]: 2

  Available templates:
   1. bug_bounty        — Find bug bounty programs
   2. jobs_python       — Find Python developer jobs
   [...]

  ? Enter template name or number: 1
  ? Extra keywords to append (leave blank to skip): hackerone
  ? How many results to collect? [default: 30]: 50
  ? Time filter? [none/day/week/month/year] [none]: week
  ? Validate URLs with HTTP check? [y/N]: n
  ? Export formats (comma-separated: json,csv,txt,html) [blank = none]: json,html
  ? Proxy URL (e.g. http://127.0.0.1:8080) [blank = none]: 
  ? Min delay between requests in seconds [default: 2.5]: 5
  ? Save raw HTML responses for debugging? [y/N]: n

  Configuration built. Starting search…
```

---

## 🔧 Command-Line Reference

### Search Modes
```
-q, --query QUERY          Raw Google dork query
--site DOMAIN              Restrict to specific domain
--dork DORK                Dork keywords (use with --site)
--template NAME            Use pre-built template
--extra KEYWORDS           Append to template queries
--list-templates           Show all templates and exit
-i, --interactive          Launch interactive mode
```

### Search Options
```
--count N                  Target result count (default: 50)
--max-requests N           Hard cap on HTTP requests (default: 100)
--time-range RANGE         Filter by time: day|week|month|year
--validate                 HTTP-validate each URL
--timeout SECS             Request timeout (default: 15)
```

### Rate Limiting
```
--delay SECS               Min delay between requests (default: 2.5)
--max-delay SECS           Max backoff delay (default: 60)
```

### Proxy Settings
```
--proxy URL                Single proxy URL
--proxy-file PATH          File with one proxy per line
```

### Output
```
--export FORMATS           Comma-separated: json,csv,txt,html
--output-dir DIR           Export directory (default: dorksentry_output)
-v, --verbose              Enable debug output
--debug-html               Save raw HTML responses
```

---

## 📚 Dork Templates

### Available Templates

| Template | Description | Query Count |
|----------|-------------|-------------|
| `bug_bounty` | Find bug bounty programs | 4 |
| `jobs_python` | Python developer jobs | 3 |
| `jobs_general` | General job postings | 3 |
| `exposed_docs` | Exposed documents (PDF/DOCX/XLSX) | 3 |
| `login_pages` | Login and admin panels | 3 |
| `api_docs` | API documentation | 3 |
| `config_files` | Exposed config files (.env, .ini) | 3 |
| `wordpress` | WordPress-specific paths | 3 |
| `directories` | Open directory listings | 3 |
| `databases` | Exposed database files | 3 |
| `cameras` | Publicly accessible cameras | 3 |
| `cloud_storage` | AWS S3, Azure Blob, GCS buckets | 3 |

### Template Details

#### `bug_bounty`
```
intext:"bug bounty" inurl:security
intext:"vulnerability disclosure" inurl:security
intext:"responsible disclosure" inurl:security
"submit vulnerability" "reward"
```

#### `exposed_docs`
```
filetype:pdf confidential
filetype:docx "not for distribution"
filetype:xlsx financial OR budget
```

#### `config_files`
```
filetype:env "DB_PASSWORD"
filetype:config intext:"password"
ext:ini "database"
```

---

## 📊 Export Formats

### JSON
**File:** `dorksentry_results_YYYYMMDD_HHMMSS.json`

```json
{
  "metadata": {
    "query": ["site:example.com inurl:admin"],
    "timestamp": "2024-01-15T10:30:00.123456",
    "total_results": 42,
    "unique_domains": 8,
    "elapsed_seconds": 23.45
  },
  "results": [
    {
      "url": "https://example.com/admin",
      "title": "Admin Login",
      "description": "Administrative access panel...",
      "domain": "example.com",
      "query": "site:example.com inurl:admin",
      "valid": true,
      "status_code": 200,
      "timestamp": "2024-01-15T10:30:05.678901"
    }
  ]
}
```

### CSV
**File:** `dorksentry_results_YYYYMMDD_HHMMSS.csv`

```csv
URL,Title,Description,Domain,Query,Valid,StatusCode,Timestamp
https://example.com/admin,Admin Login,Administrative access...,example.com,site:example.com inurl:admin,True,200,2024-01-15T10:30:05.678901
```

### TXT
**File:** `dorksentry_results_YYYYMMDD_HHMMSS.txt`

```
https://example.com/admin
https://example.com/login
https://test.example.com/dashboard
```

One URL per line — perfect for piping to other tools.

### HTML
**File:** `dorksentry_results_YYYYMMDD_HHMMSS.html`

Beautiful interactive report with:
- Metadata cards (total results, domains, elapsed time)
- Sortable table with click tracking
- Color-coded validation status
- Dark theme styling
- Self-contained (no external dependencies)

**Screenshot:**
```
┌─────────────────────────────────────────────────┐
│  🔍 DorkSentry Report                          │
│  Generated: 2024-01-15T10:30:00 UTC            │
├─────────────────────────────────────────────────┤
│  [42 Results] [8 Domains] [35 Valid] [23.45s]  │
├─────────────────────────────────────────────────┤
│  # | Title / URL                    | Status   │
│  1 | Admin Login                    | ✓ Live   │
│    | https://example.com/admin      | HTTP 200 │
│  2 | Dashboard                      | ✓ Live   │
│    | https://test.example.com/dash  | HTTP 200 │
└─────────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Problem: "0 results collected"

**Possible causes:**

1. **Google CAPTCHA / Block Page**
   - **Solution:** Increase `--delay` to 10-15s
   - **Solution:** Use `--proxy` or `--proxy-file`
   - **Solution:** Wait 15-30 minutes before retrying

2. **Query Returned No Results**
   - **Solution:** Test query manually on google.com
   - **Solution:** Simplify query (remove complex operators)

3. **CSS Selectors Outdated**
   - **Solution:** Run with `--debug-html --verbose`
   - **Solution:** Open `google_response_debug.html` in browser
   - **Solution:** Report issue with HTML sample

### Problem: CAPTCHA Detection

**Symptoms:**
```
[WARN]  CAPTCHA/block page detected! Google is blocking requests.
  → Try: increase --delay to 10+, use --proxy, or wait before retrying.
```

**Solutions (in order of effectiveness):**

1. **Increase delay:**
   ```bash
   python dorksentry.py -q "query" --delay 15 --max-delay 60
   ```

2. **Use Tor proxy:**
   ```bash
   # Install Tor, then:
   python dorksentry.py -q "query" --proxy "socks5://127.0.0.1:9050" --delay 10
   ```

3. **Rotate proxies:**
   ```bash
   python dorksentry.py -q "query" --proxy-file proxies.txt --delay 5
   ```

4. **Wait and retry:**
   - Google blocks are usually temporary (15-60 minutes)
   - Clear cookies: `rm -rf ~/.dorksentry_agreed` (forces disclaimer re-acceptance)

### Problem: "Unexpected HTTP 429"

**Cause:** Google rate limit (Too Many Requests)

**Solution:**
```bash
# Automatic backoff is enabled, but you can help by:
python dorksentry.py -q "query" \
    --delay 20 \
    --max-delay 120 \
    --max-requests 20  # Lower request cap
```

### Problem: Validation Fails

**Symptoms:**
```
[INFO]  Validating 50 URLs …
[OK]    Validation complete: 0/50 reachable.
```

**Possible causes:**
- URLs require authentication
- Target sites are down
- Validation timeout too short

**Solution:**
```bash
python dorksentry.py -q "query" \
    --validate \
    --timeout 30  # Increase from default 15s
```

### Debug Mode Workflow

When something goes wrong:

```bash
# 1. Run with full diagnostics
python dorksentry.py -q "query" \
    --debug-html \
    --verbose \
    --delay 10

# 2. Check console output for:
#    - CSS selector match counts
#    - HTML statistics (divs, links, size)
#    - Page title

# 3. Open google_response_debug.html in browser
#    Look for:
#    - "Before you continue" → Consent page
#    - "unusual traffic" → CAPTCHA
#    - "Sorry..." → Soft block
#    - Normal search results → Selector issue

# 4. Report issue with:
#    - Full command used
#    - Console output
#    - First 50 lines of debug HTML
```

---

## 💡 Best Practices

### Rate Limiting
- **Start conservative:** `--delay 5` minimum for first run
- **Monitor output:** If you see CAPTCHAs, double the delay
- **Use proxies for large jobs:** 200+ results
- **Respect robots.txt:** This tool is for research, not abuse

### Query Design
- **Start broad, then narrow:** Test with `site:example.com` first
- **Combine operators:** `site:example.com (inurl:admin OR inurl:login) filetype:php`
- **Use templates as inspiration:** Modify existing templates for your needs
- **Test manually first:** Verify query works on google.com

### Result Validation
- **Validate only when needed:** Adds significant time (0.3s per URL)
- **Use for critical findings:** Bug bounty, vulnerability research
- **Skip for recon:** When you just need a URL list

### Export Strategy
- **JSON for analysis:** Import into Python/jq for further processing
- **CSV for spreadsheets:** Open in Excel/Google Sheets
- **HTML for reports:** Share with team or include in documentation
- **TXT for piping:** Feed URLs into other tools

### Operational Security
- **Use VPNs/proxies for sensitive research**
- **Don't hit the same target repeatedly**
- **Rotate IP addresses for large campaigns**
- **Keep logs for attribution** (in case of false positives)

---

## 📝 Examples

### Example 1: Bug Bounty Reconnaissance

```bash
# Find HackerOne programs accepting submissions
python dorksentry.py \
    --template bug_bounty \
    --extra "hackerone" \
    --count 100 \
    --validate \
    --export json,html \
    --delay 5
```

**Output:**
- `dorksentry_output/dorksentry_results_20240115_103000.json`
- `dorksentry_output/dorksentry_results_20240115_103000.html`

---

### Example 2: Exposed Configuration Files

```bash
# Find .env files with database credentials
python dorksentry.py \
    -q 'filetype:env "DB_PASSWORD" -site:github.com -site:gitlab.com' \
    --count 50 \
    --time-range month \
    --export json,csv \
    --delay 10
```

**Why exclude GitHub/GitLab?**
- Reduces noise (legitimate public repos)
- Focuses on misconfigured servers

---

### Example 3: Site-Specific Audit

```bash
# Audit example.com for exposed admin panels
python dorksentry.py \
    --site example.com \
    --dork "inurl:admin OR inurl:login OR inurl:dashboard" \
    --validate \
    --export html \
    --delay 3
```

---

### Example 4: Job Search Aggregation

```bash
# Find remote Python jobs posted this week
python dorksentry.py \
    --template jobs_python \
    --extra "remote senior" \
    --time-range week \
    --count 200 \
    --export csv \
    --delay 5
```

**Use case:** Import CSV into spreadsheet, filter by salary/location

---

### Example 5: OSINT on Cloud Storage

```bash
# Find exposed AWS S3 buckets
python dorksentry.py \
    -q 'site:s3.amazonaws.com intitle:"index of"' \
    --count 100 \
    --validate \
    --export json,txt \
    --delay 8 \
    --proxy-file proxies.txt
```

**Ethical note:** Only access buckets you're authorized to test.

---

### Example 6: Academic Research

```bash
# Find publicly available datasets
python dorksentry.py \
    -q 'filetype:csv OR filetype:json "dataset" site:edu' \
    --time-range year \
    --count 150 \
    --export json,html \
    --delay 5
```

---

### Example 7: Stealth Mode (Maximum Evasion)

```bash
# Low-profile search with Tor
python dorksentry.py \
    -q "sensitive research query" \
    --proxy "socks5://127.0.0.1:9050" \
    --delay 20 \
    --max-delay 120 \
    --count 30 \
    --max-requests 15 \
    --timeout 30
```

**Settings explained:**
- Tor proxy for anonymity
- 20s delay (conservative)
- Max 15 requests (avoid pattern detection)
- 30s timeout (Tor can be slow)

---

## 🔬 Development

### Architecture

**Single-file design:**
```
dorksentry.py (2000+ lines)
├── Imports & Metadata
├── Constants (User-Agents, Templates, Colors)
├── Data Classes (SearchResult, Configuration)
├── Utility Classes (ColorPrinter, RateLimiter, ProxyManager)
├── Core Engine (GoogleSearcher)
├── Result Processing (Validation, Stats, Deduplication)
├── Export Handlers (JSON, CSV, TXT, HTML)
├── CLI (ArgumentParser, Interactive Mode)
└── Main Execution Loop
```

### Key Classes

**GoogleSearcher:**
- Handles HTTP requests to Google
- Parses HTML with BeautifulSoup
- Implements pagination
- Detects CAPTCHAs
- Rotates user-agents

**RateLimiter:**
- Exponential backoff algorithm
- Jitter to avoid fingerprinting
- Automatic reset on success

**ProxyManager:**
- Round-robin rotation
- Supports HTTP/HTTPS/SOCKS5
- File-based pool loading

**ResultValidator:**
- HEAD → GET fallback
- Handles timeouts gracefully
- Updates SearchResult objects in-place

### HTML Selectors (2024 Update)

Google's HTML structure as of January 2024:

```python
_CONTAINER_SELECTORS = [
    "div[data-hveid][data-ved]",    # Most reliable (attribute combo)
    "div.MjjYud",                    # 2024 outer wrapper
    "div.g.Ww4FFb",                  # Common variant
    "div.tF2Cxc",                    # Legacy but still works
    "div.g",                         # Fallback
    "div[jscontroller]",             # Broadest fallback
]
```

**If selectors break:**
1. Run with `--debug-html --verbose`
2. Inspect `google_response_debug.html`
3. Find new wrapper classes (usually `div` with unique class)
4. Update `_CONTAINER_SELECTORS` priority order

### CAPTCHA Detection Patterns

```python
indicators = [
    "unusual traffic",           # Classic CAPTCHA
    "captcha", "recaptcha",      # Explicit CAPTCHA
    "before you continue",       # Consent page
    "our systems have detected", # Soft block
    "sorry/index",               # Rate limit redirect
    "consent.google",            # EU consent requirement
    "automated queries",         # Bot detection
]
```

---

## 🤝 Contributing

### Reporting Issues

**Good issue report:**
```markdown
**Environment:**
- OS: Ubuntu 22.04
- Python: 3.10.6
- DorkSentry: v1.0.1

**Command:**
```bash
python dorksentry.py -q "site:example.com" --debug-html --verbose
```

**Expected:** 10+ results
**Actual:** 0 results

**Console Output:**
```
[INFO]  Searching: site:example.com
[DBG]   Selector 'div.g' matched 0 containers.
[DBG]   Page title: 'Before you continue' | divs=23 | links=5 | html_size=1842 bytes
[WARN]  CAPTCHA/block page detected!
```

**Debug HTML:** (attach first 100 lines)
```

### Feature Requests

**Desired features:**
- [ ] Google API integration (official API support)
- [ ] Shodan/Censys integration
- [ ] SQLite result storage
- [ ] Resume interrupted searches
- [ ] Scheduled/cron mode
- [ ] Docker container

**Open an issue with:**
- Use case description
- Expected behavior
- Mockup of desired output

### Pull Requests

**Contributing code:**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/google-api`
3. Follow existing code style (PEP 8)
4. Add docstrings to new functions
5. Test with `--debug-html --verbose`
6. Update README if adding features
7. Submit PR with clear description

---

## 📄 License

**MIT License**

```
Copyright (c) 2024 DorkSentry Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **BeautifulSoup4** — HTML parsing library
- **Requests** — HTTP library
- **Google** — Search engine (use responsibly)
- **OSINT Community** — Inspiration and techniques
- **Bug Bounty Hunters** — Testing and feedback

---

## 📞 Support

### Documentation
- **This README** — Comprehensive guide
- **Built-in help:** `python dorksentry.py --help`
- **Template list:** `python dorksentry.py --list-templates`

### Community
- **Issues:** [GitHub Issues](https://github.com/yourusername/dorksentry/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/dorksentry/discussions)

### Professional Use
For commercial support, custom development, or security audits, contact: **[email protected]**

---

## 🔐 Security Notice

**Vulnerability Disclosure:**
If you discover a security vulnerability in DorkSentry itself, please email **[email protected]** with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment

We will respond within 48 hours and credit you in the advisory (if desired).

---

## 📊 Statistics

```
Lines of Code:    2000+
Classes:          10
Functions:        45+
Dork Templates:   12
Export Formats:   4
User-Agents:      25
Supported Python: 3.7+
Dependencies:     2 (requests, beautifulsoup4)
```

---

## 🗺️ Roadmap

### v1.1 (Planned)
- [ ] Google Custom Search API support
- [ ] SQLite result database
- [ ] Resume interrupted searches
- [ ] Configurable selector presets

### v1.2 (Planned)
- [ ] Shodan integration
- [ ] Censys integration
- [ ] Advanced deduplication (fuzzy matching)
- [ ] Custom export templates

### v2.0 (Future)
- [ ] Multi-engine support (Bing, DuckDuckGo)
- [ ] Web UI dashboard
- [ ] Scheduled/cron mode
- [ ] Result correlation engine

---

**Made with ❤️ for the OSINT and security research community**

```
     ____             _    ____            _              
    |  _ \  ___  _ __| | _/ ___|  ___ _ __ | |_ _ __ _   _ 
    | | | |/ _ \| '__| |/ /\___ \ / _ \ '_ \| __| '__| | | |
    | |_| | (_) | |  |   <  ___) |  __/ | | | |_| |  | |_| |
    |____/ \___/|_|  |_|\_\|____/ \___|_| |_|\__|_|   \__, |
                                                        |___/ 
                v1.0.1 — Use Responsibly
```

---

**Last Updated:** January 2024  
**Maintained By:** DorkSentry Project  
**Status:** Active Development
```

This README is comprehensive, professional, and covers:
- Complete feature overview
- Installation and setup
- Detailed usage examples
- Troubleshooting guide
- Best practices
- Contributing guidelines
- Legal disclaimers

Ready to be published alongside your tool! 🎯
