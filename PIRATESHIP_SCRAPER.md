# Pirate Ship Scraper (Playwright)

This module uses [Playwright](https://playwright.dev/python/) to automate the browser and scrape or interact with [Pirate Ship](https://ship.pirateship.com).

## Setup

1. **Install Python dependency**
   ```bash
   pip install playwright
   ```

2. **Install browser (required once)**

   **On Ubuntu/Debian (apt):**
   ```bash
   playwright install chromium
   ```
   If system deps are missing, run: `playwright install-deps chromium`

   **On CentOS/RHEL/Amazon Linux (yum):**  
   Playwright’s installer uses apt-get by default. On yum-based systems, install dependencies with yum first, then install the browser:

   ```bash
   # Install Chromium dependencies (yum)
   sudo yum install -y atk at-spi2-atk cups-libs libdrm libxcb libxkbcommon at-spi2-core \
     libX11 libXcomposite libXdamage libXext libXfixes libXrandr mesa-libgbm pango cairo alsa-lib

   # Then install the browser binary only (no apt)
   playwright install chromium
   ```

   Or run the provided script (from repo root):
   ```bash
   chmod +x scripts/playwright-install-yum.sh
   ./scripts/playwright-install-yum.sh
   ```

3. **Credentials** (use env vars; do not commit real credentials)
   - `PIRATESHIP_EMAIL` – your Pirate Ship login email
   - `PIRATESHIP_PASSWORD` – your Pirate Ship password  

   Or pass `email` and `password` into the functions.

### How to set the variables

**Option A – Current terminal only (temporary)**
```bash
export PIRATESHIP_EMAIL="your-email@example.com"
export PIRATESHIP_PASSWORD="your-password"
```
Then run your script in the same terminal. They disappear when you close the terminal.

**Option B – `.env` file (load before running)**
Create a file named `.env` in the project root (same folder as `app.py`):
```
PIRATESHIP_EMAIL=your-email@example.com
PIRATESHIP_PASSWORD=your-password
```
No quotes needed. Then load it before running:
```bash
set -a
source .env
set +a
python3 your_script.py
```
Or in one line: `export $(grep -v '^#' .env | xargs)` then run your app.  
**Important:** Add `.env` to `.gitignore` so you never commit it:
```bash
echo ".env" >> .gitignore
```

**Option C – Shell profile (persistent for your user)**
Add to `~/.bashrc` or `~/.profile`:
```bash
export PIRATESHIP_EMAIL="your-email@example.com"
export PIRATESHIP_PASSWORD="your-password"
```
Then run `source ~/.bashrc` (or open a new terminal). Every new shell will have these set.

**Option D – Systemd service (if the app runs as a service)**
In your `.service` file, under `[Service]`:
```ini
Environment="PIRATESHIP_EMAIL=your-email@example.com"
Environment="PIRATESHIP_PASSWORD=your-password"
```
Or use `EnvironmentFile=/path/to/.env` to point at a file that contains those two lines.

## Run (with verbosity)

From the project root, set credentials and run with verbose output to see where it gets stuck.

**Linux / macOS:**
```bash
export PIRATESHIP_EMAIL="your-email@example.com"
export PIRATESHIP_PASSWORD="your-password"
export PIRATESHIP_VERBOSE=1
python3 pirateship_scraper.py
```
If you use a `.env` file: `set -a && source .env && set +a && export PIRATESHIP_VERBOSE=1 && python3 pirateship_scraper.py`

**Windows (PowerShell):**
```powershell
$env:PIRATESHIP_EMAIL = "your-email@example.com"
$env:PIRATESHIP_PASSWORD = "your-password"
$env:PIRATESHIP_VERBOSE = "1"
python pirateship_scraper.py
```

**Windows (cmd):**
```cmd
set PIRATESHIP_EMAIL=your-email@example.com
set PIRATESHIP_PASSWORD=your-password
set PIRATESHIP_VERBOSE=1
python pirateship_scraper.py
```

Optional args: `python3 pirateship_scraper.py <from_zip> <to_zip> <weight_oz>` (default: 90210 10001 16.0).

**Shipment report by eBay order ID** (Playwright only):
```bash
export PIRATESHIP_VERBOSE=1
python3 pirateship_scraper.py report 17-14149-65322
```
The scraper logs in with Playwright (browser), navigates to the report URL, waits for the shipment grid to render, then returns the page HTML and parsed cost, shipment_url, has_shipment_span (and `html`, `frame_htmls` in the result dict).

Verbose output shows each step (login, navigate, wait for grid, parsed fields).

## Usage

### From async code
```python
import asyncio
from pirateship_scraper import get_rates, login, get_page_after_login

# Get shipping rates (login + fill form + scrape rates)
result = asyncio.run(get_rates("90210", "10001", 16.0))
if result["success"]:
    for r in result["rates"]:
        print(r)
else:
    print(result["error"])

# Or just login and get a page’s HTML for custom scraping
result = asyncio.run(get_page_after_login(path="/ship"))
print(result["html"][:500])
```

### From sync code
```python
from pirateship_scraper import get_rates, run_async

result = run_async(get_rates("90210", "10001", 16.0, headless=True))
# With progress messages (or set env PIRATESHIP_VERBOSE=1):
result = run_async(get_rates("90210", "10001", 16.0, verbose=True))
```

### Optional: dimensions
```python
result = run_async(get_rates(
    "90210", "10001", 16.0,
    length_in=12, width_in=9, height_in=6
))
```

## Selectors

Pirate Ship’s HTML can change. The scraper uses generic selectors (`input[name*="..."]`, etc.). If login or rate scraping fails, inspect the live site and update selectors in `pirateship_scraper.py` (e.g. in `login()` and `get_rates()`).

**If you see “Timeout … waiting for … email”:** The scraper uses the login page at [https://ship.pirateship.com/](https://ship.pirateship.com/). If the page loads slowly or the form structure changes, run with `headless=False` to watch the browser and confirm the form appears; adjust selectors in `login()` if needed.

## Disclaimer

- Scraping may violate Pirate Ship’s Terms of Service. Check their ToS and use at your own risk.
- Prefer an official Pirate Ship API if one is available.
- Keep credentials in environment variables or a secure config; do not commit them.
