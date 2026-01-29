# Pirate Ship Scraper (Playwright)

This module uses [Playwright](https://playwright.dev/python/) to automate the browser and scrape or interact with [Pirate Ship](https://www.pirateship.com).

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

## Disclaimer

- Scraping may violate Pirate Ship’s Terms of Service. Check their ToS and use at your own risk.
- Prefer an official Pirate Ship API if one is available.
- Keep credentials in environment variables or a secure config; do not commit them.
