"""
Pirate Ship scraper using Playwright.

Uses browser automation to log in and scrape/ interact with pirateship.com.
Credentials: set PIRATESHIP_EMAIL and PIRATESHIP_PASSWORD in environment,
or pass them to login().

Note: Scraping may violate Pirate Ship's Terms of Service. Prefer an official
API if available. Use responsibly and at your own risk.
"""

import os
import re
import asyncio
from typing import Optional, Dict, Any, List


# Base URL for Pirate Ship; login page is the root: https://ship.pirateship.com/
PIRATESHIP_BASE = "https://ship.pirateship.com"


def _log(verbose: bool, msg: str) -> None:
    if verbose:
        print(f"[pirateship] {msg}")


async def _get_browser(headless: bool = True):
    """Launch Playwright browser. Install with: playwright install chromium"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError("Install playwright: pip install playwright && playwright install chromium")
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=headless)
    return p, browser


def _verbose_default() -> bool:
    return os.environ.get("PIRATESHIP_VERBOSE", "").lower() in ("1", "true", "yes")


async def login(
    email: Optional[str] = None,
    password: Optional[str] = None,
    headless: bool = True,
    verbose: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Log in to Pirate Ship and return context (page, browser) for further actions.
    Email/password default to env PIRATESHIP_EMAIL, PIRATESHIP_PASSWORD.
    Set verbose=True or PIRATESHIP_VERBOSE=1 for progress messages.
    """
    verbose = verbose if verbose is not None else _verbose_default()
    email = email or os.environ.get("PIRATESHIP_EMAIL")
    password = password or os.environ.get("PIRATESHIP_PASSWORD")
    if not email or not password:
        return {"success": False, "error": "PIRATESHIP_EMAIL and PIRATESHIP_PASSWORD required"}

    p = None
    browser = None
    try:
        _log(verbose, "Launching browser...")
        p, browser = await _get_browser(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()
        page.set_default_timeout(30000)  # 30s for navigation and slow loads

        _log(verbose, f"Navigating to {PIRATESHIP_BASE}/ ...")
        await page.goto(PIRATESHIP_BASE + "/", wait_until="domcontentloaded")
        _log(verbose, "Waiting for JS/SPA (0.5s)...")
        await asyncio.sleep(0.5)
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            _log(verbose, f"networkidle skipped: {e}")
        await asyncio.sleep(0.3)

        find_timeout_ms = 15000  # 15s to find email/password
        _log(verbose, f"Looking for email field (timeout {find_timeout_ms}ms)...")

        email_filled = False
        for selector in [
            'input[type="email"]',
            'input[name="email"]',
            'input[autocomplete="email"]',
            'input[id*="email"]',
            'input[placeholder*="mail" i]',
            'input[placeholder*="Email"]',
            'input[placeholder*="address" i]',
            'form input[type="text"]',  # some sites use type=text for email
        ]:
            try:
                _log(verbose, f"  Trying selector: {selector}")
                el = page.locator(selector).first
                await el.wait_for(state="visible", timeout=find_timeout_ms)
                await el.fill(email)
                _log(verbose, f"  Filled email with selector: {selector}")
                email_filled = True
                break
            except Exception as e:
                _log(verbose, f"  Skip ({selector}): {e}")
                continue
        if not email_filled:
            _log(verbose, "Trying fallbacks (label/placeholder/role)...")
            fallbacks = [
                ("get_by_label(Email)", lambda: page.get_by_label("Email", exact=False).fill(email)),
                ("get_by_label(email)", lambda: page.get_by_label("email", exact=False).fill(email)),
                ("get_by_placeholder(Email)", lambda: page.get_by_placeholder("Email").fill(email)),
                ("get_by_placeholder(Email address)", lambda: page.get_by_placeholder("Email address").fill(email)),
                ("get_by_placeholder(email)", lambda: page.get_by_placeholder("email").fill(email)),
                ("get_by_role(textbox, name=email)", lambda: page.get_by_role("textbox", name=re.compile(r"email", re.I)).first.fill(email)),
            ]
            for name, fn in fallbacks:
                try:
                    _log(verbose, f"  Trying {name}")
                    await fn()
                    _log(verbose, f"  Filled email with: {name}")
                    email_filled = True
                    break
                except Exception as e:
                    _log(verbose, f"  Skip ({name}): {e}")
        if not email_filled:
            _log(verbose, "ERROR: No email field found.")
            await browser.close()
            await p.stop()
            return {"success": False, "error": "Could not find email input on login page. Site structure may have changed."}

        _log(verbose, "Looking for password field...")
        password_filled = False
        for selector in [
            'input[type="password"]',
            'input[name="password"]',
            'input[autocomplete="current-password"]',
            'input[id*="password"]',
            'input[placeholder*="assword"]',
        ]:
            try:
                _log(verbose, f"  Trying selector: {selector}")
                el = page.locator(selector).first
                await el.wait_for(state="visible", timeout=find_timeout_ms)
                await el.fill(password)
                _log(verbose, f"  Filled password with selector: {selector}")
                password_filled = True
                break
            except Exception as e:
                _log(verbose, f"  Skip ({selector}): {e}")
                continue
        if not password_filled:
            try:
                _log(verbose, "  Trying get_by_label(Password)")
                await page.get_by_label("Password", exact=False).fill(password)
                password_filled = True
            except Exception as e:
                _log(verbose, f"  Skip (Password label): {e}")
        if not password_filled:
            _log(verbose, "ERROR: No password field found.")
            await browser.close()
            await p.stop()
            return {"success": False, "error": "Could not find password input on login page."}

        _log(verbose, "Submitting login form...")
        for selector in [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Log in")',
            'button:has-text("Sign in")',
            'button:has-text("Login")',
            '[data-testid="login-submit"]',
            'form button[type="submit"]',
            'a[href*="login"] + button',
        ]:
            try:
                await page.locator(selector).first.click(timeout=5000)
                _log(verbose, f"Clicked submit: {selector}")
                break
            except Exception:
                continue

        _log(verbose, "Waiting for post-login load...")
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(0.3)

        url = page.url
        _log(verbose, f"Current URL: {url}")
        if "login" in url:
            _log(verbose, "ERROR: Still on login page.")
            await browser.close()
            await p.stop()
            return {"success": False, "error": "Login failed (still on login page)"}
        _log(verbose, "Login succeeded.")
        return {
            "success": True,
            "page": page,
            "context": context,
            "browser": browser,
            "playwright": p,
        }
    except Exception as e:
        _log(verbose, f"ERROR: {e}")
        if browser:
            await browser.close()
        if p:
            await p.stop()
        return {"success": False, "error": str(e)}


async def get_rates(
    from_zip: str,
    to_zip: str,
    weight_oz: float,
    length_in: Optional[float] = None,
    width_in: Optional[float] = None,
    height_in: Optional[float] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    headless: bool = True,
    verbose: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Log in, open the rate-check flow, fill origin/dest/weight (and dimensions if provided),
    then scrape the displayed rates.
    Returns { "success": bool, "rates": [...], "error": str }.
    Set verbose=True or PIRATESHIP_VERBOSE=1 for progress messages.
    """
    verbose = verbose if verbose is not None else _verbose_default()
    result = await login(email=email, password=password, headless=headless, verbose=verbose)
    if not result.get("success"):
        return {"success": False, "rates": [], "error": result.get("error", "Login failed")}

    page = result["page"]
    browser = result["browser"]
    p = result["playwright"]
    rates: List[Dict[str, Any]] = []

    try:
        _log(verbose, "Navigating to /ship ...")
        await page.goto(f"{PIRATESHIP_BASE}/ship", wait_until="domcontentloaded")
        await asyncio.sleep(0.1)

        _log(verbose, "Filling origin/destination/weight...")
        zip_selectors = [
            'input[name*="origin"]', 'input[name*="from"]', 'input[placeholder*="origin"]',
            'input[placeholder*="zip"]', '[data-testid="origin-zip"]',
        ]
        for sel in zip_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.fill(from_zip)
                    break
            except Exception:
                continue

        to_zip_selectors = [
            'input[name*="destination"]', 'input[name*="to"]', 'input[placeholder*="destination"]',
            '[data-testid="destination-zip"]',
        ]
        for sel in to_zip_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.fill(to_zip)
                    break
            except Exception:
                continue

        weight_selectors = [
            'input[name*="weight"]', 'input[placeholder*="weight"]', '[data-testid="weight"]',
        ]
        for sel in weight_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.fill(str(weight_oz))
                    break
            except Exception:
                continue

        if length_in is not None and width_in is not None and height_in is not None:
            for name, val in [("length", length_in), ("width", width_in), ("height", height_in)]:
                try:
                    el = await page.query_selector(f'input[name*="{name}"]')
                    if el:
                        await el.fill(str(val))
                except Exception:
                    pass

        _log(verbose, "Clicking Get rates...")
        await page.click('button:has-text("Get rates"), button:has-text("Rates"), [data-testid="get-rates"]')
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            await asyncio.sleep(0.5)

        _log(verbose, "Scraping rate rows...")
        rate_cards = await page.query_selector_all('[data-testid="rate"], .rate-card, .carrier-rate, table.rates tbody tr')
        for card in rate_cards:
            text = await card.inner_text()
            lines = [t.strip() for t in text.split("\n") if t.strip()]
            if lines:
                rates.append({"raw_lines": lines, "text": text.strip()})

        if not rates:
            # Fallback: grab any price-like elements
            body = await page.inner_text("body")
            rates.append({"raw_lines": [body[:2000]], "text": body[:2000]})

        _log(verbose, f"Done. Found {len(rates)} rate(s).")
        await browser.close()
        await p.stop()
        return {"success": True, "rates": rates}
    except Exception as e:
        _log(verbose, f"ERROR: {e}")
        try:
            await browser.close()
            await p.stop()
        except Exception:
            pass
        return {"success": False, "rates": [], "error": str(e)}


# Regex for common tracking number formats (USPS 94..., UPS 1Z..., FedEx 12+ digits)
_TRACKING_PATTERN = re.compile(
    r"\b(94\d{20,22}|1Z[A-Z0-9]{16}|(?:\d{12,22}))\b"
)
# Dollar amount: $4.88 or $ 4.88, or "4.88" in price context (capture numeric part)
_COST_PATTERN = re.compile(r"\$\s*(\d+\.\d{2})\b|(?:cost|total|price|amount)[\s:]*\$?\s*(\d+\.\d{2})\b", re.I)
# Batch/shipment link on report page: https://ship.pirateship.com/batch/546611907/shipment/694491791
_BATCH_SHIPMENT_URL_PATTERN = re.compile(
    r"https?://ship\.pirateship\.com/batch/\d+/shipment/\d+",
    re.I,
)


def get_shipment_report(
    ebay_order_id: str,
    email: Optional[str] = None,
    password: Optional[str] = None,
    verbose: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Fetch the reports/shipment page using Python requests (no Playwright).
    Session: GET login page → POST login (tries common endpoints) → GET report URL.
    Returns { "success", "html", "url", "cost", "shipment_url", "has_shipment_span", "shipment_span_text", "shipments", "frame_htmls", "status_code", "error" }.
    Example URL: reports/shipment?tracking=SEARCH_TERM_<ebay_order_id>
    """
    try:
        import requests
    except ImportError:
        return {"success": False, "error": "requests library required", "html": "", "url": "", "cost": None, "shipment_url": None, "has_shipment_span": False, "shipment_span_text": None}
    verbose = verbose if verbose is not None else _verbose_default()
    email = email or os.environ.get("PIRATESHIP_EMAIL")
    password = password or os.environ.get("PIRATESHIP_PASSWORD")
    if not email or not password:
        return {"success": False, "error": "PIRATESHIP_EMAIL and PIRATESHIP_PASSWORD required", "html": "", "url": "", "cost": None, "shipment_url": None, "has_shipment_span": False, "shipment_span_text": None}

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": PIRATESHIP_BASE,
        "Referer": f"{PIRATESHIP_BASE}/",
    })

    # 1) GET login page (https://ship.pirateship.com/) to obtain cookies
    _log(verbose, f"GET login page {PIRATESHIP_BASE}/ ...")
    login_page = session.get(f"{PIRATESHIP_BASE}/", timeout=30)
    login_page.raise_for_status()
    login_html = login_page.text
    _log(verbose, f"  cookies: {list(session.cookies.keys())}")

    # 2) Find login form action from page (if present)
    form_action = None
    m = re.search(r'<form[^>]*\s+action=["\']([^"\']+)["\']', login_html, re.I)
    if m:
        form_action = m.group(1).strip()
        if form_action.startswith("/"):
            form_action = f"{PIRATESHIP_BASE}{form_action}"
        elif not form_action.startswith("http"):
            form_action = f"{PIRATESHIP_BASE}/{form_action}"
        _log(verbose, f"  Found form action: {form_action}")

    # 3) Try to log in: POST to form action or root, form-encoded (HTML forms use application/x-www-form-urlencoded)
    logged_in = False
    # Build list: (url, data_dict, description)
    login_tries = []
    if form_action:
        login_tries.append((form_action, {"email": email, "password": password}, f"form action"))
    login_tries.append((f"{PIRATESHIP_BASE}/", {"email": email, "password": password}, "POST /"))
    for url_suffix in ["/login", "/api/auth/login", "/api/login", "/auth/login", "/session"]:
        login_tries.append((f"{PIRATESHIP_BASE}{url_suffix}", {"email": email, "password": password}, url_suffix))
    login_tries.append((f"{PIRATESHIP_BASE}/", {"username": email, "password": password}, "POST / (username)"))

    for url, data, desc in login_tries:
        _log(verbose, f"  Try login POST {desc}...")
        try:
            r = session.post(url, data=data, timeout=15)
            _log(verbose, f"    status={r.status_code}, url={r.url}")
            if r.status_code in (200, 302, 303):
                logged_in = True
                break
        except Exception as e:
            _log(verbose, f"    error: {e}")
    if not logged_in:
        _log(verbose, "  No successful login response; continuing to try report URL with current cookies.")

    # 3) GET reports/shipment URL
    search_term = f"SEARCH_TERM_{ebay_order_id}"
    report_url = f"{PIRATESHIP_BASE}/reports/shipment?tracking={search_term}"
    _log(verbose, f"GET report: {report_url}")
    try:
        r = session.get(report_url, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        return {"success": False, "error": str(e), "html": "", "url": report_url, "cost": None, "shipment_url": None, "has_shipment_span": False, "shipment_span_text": None}
    html = r.text
    final_url = r.url

    # 4) Parse same as Playwright path
    cost = None
    cost_match = _COST_PATTERN.search(html)
    if cost_match:
        amount = cost_match.group(1) or cost_match.group(2)
        if amount:
            try:
                cost = float(amount)
            except ValueError:
                pass
    if cost is None and 'e1d69dh90' in html:
        m = re.search(r'class="[^"]*e1d69dh90[^"]*">\s*\$?\s*(\d+\.\d{2})', html)
        if m:
            try:
                cost = float(m.group(1))
            except ValueError:
                pass

    shipment_url = None
    m = _BATCH_SHIPMENT_URL_PATTERN.search(html)
    if m:
        shipment_url = m.group(0)
    if not shipment_url and 'href="/batch/' in html:
        m = re.search(r'href="(/batch/\d+/shipment/\d+)"', html)
        if m:
            shipment_url = f"{PIRATESHIP_BASE}{m.group(1)}"

    has_shipment_span = "ef06jtw0" in html
    shipment_span_text = None
    if has_shipment_span:
        m = re.search(r'<span[^>]*class="[^"]*ef06jtw0[^"]*"[^>]*>([^<]*)', html)
        if m:
            shipment_span_text = m.group(1).strip()

    result = {
        "success": True,
        "html": html,
        "url": final_url,
        "cost": cost,
        "shipment_url": shipment_url,
        "has_shipment_span": has_shipment_span,
        "shipment_span_text": shipment_span_text,
        "shipments": [],
        "frame_htmls": [],
        "status_code": r.status_code,
    }
    print("[pirateship] --- report output ---")
    print(f"  url: {final_url}")
    print(f"  shipment_url: {shipment_url}")
    print(f"  has_shipment_span: {has_shipment_span}")
    if shipment_span_text:
        print(f"  shipment_span_text: {shipment_span_text[:300]}{'...' if len(shipment_span_text) > 300 else ''}")
    print(f"  cost: {cost}")
    print("[pirateship] --- end report ---")
    return result


async def get_last_shipments(
    count: int = 5,
    email: Optional[str] = None,
    password: Optional[str] = None,
    headless: bool = True,
    verbose: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Log in, go to shipment history, and return the last `count` purchased shipments.
    Each item has at least tracking_number; may include date, carrier, status, raw_text.
    Returns { "success": bool, "shipments": [...], "error": str }.
    """
    verbose = verbose if verbose is not None else _verbose_default()
    result = await login(email=email, password=password, headless=headless, verbose=verbose)
    if not result.get("success"):
        return {"success": False, "shipments": [], "error": result.get("error", "Login failed")}

    page = result["page"]
    browser = result["browser"]
    p = result["playwright"]
    shipments: List[Dict[str, Any]] = []

    try:
        # Shipment history / purchased labels are at /ship (not /shipments)
        paths_to_try = ["/ship", "/history", "/labels", "/dashboard", "/"]
        html = None
        url_used = None
        for path in paths_to_try:
            _log(verbose, f"Navigating to {PIRATESHIP_BASE}{path} ...")
            try:
                await page.goto(f"{PIRATESHIP_BASE}{path}", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(0.5)
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass
                await asyncio.sleep(0.3)
                html = await page.content()
                url_used = page.url
                _log(verbose, f"Loaded {url_used}")
                break
            except Exception as e:
                _log(verbose, f"  Skip {path}: {e}")
                continue

        if not html:
            await browser.close()
            await p.stop()
            return {"success": False, "shipments": [], "error": "Could not load any shipment history page"}

        _log(verbose, "Looking for shipment rows or cards...")
        # Try to get discrete shipment rows/cards so we keep order (most recent first)
        row_selectors = [
            "table tbody tr",
            "[data-testid*='shipment']",
            "[data-testid*='label']",
            ".shipment-row",
            ".shipment-card",
            ".label-row",
            "[class*='shipment']",
            "[class*='Shipment']",
        ]
        seen_tracking: set = set()
        for selector in row_selectors:
            try:
                locs = page.locator(selector)
                n = await locs.count()
                if n == 0:
                    continue
                _log(verbose, f"  Found {n} elements for {selector}")
                for i in range(min(n, count * 2)):  # get a few extra in case of dupes
                    try:
                        el = locs.nth(i)
                        text = await el.inner_text()
                        if not text or len(text) > 2000:
                            continue
                        # Find first tracking number in this row/card
                        match = _TRACKING_PATTERN.search(text)
                        if match:
                            tn = match.group(1)
                            if tn in seen_tracking:
                                continue
                            seen_tracking.add(tn)
                            # Heuristic: USPS 94..., UPS 1Z...
                            carrier = "USPS" if tn.startswith("94") else ("UPS" if tn.startswith("1Z") else "Unknown")
                            shipments.append({
                                "tracking_number": tn,
                                "carrier": carrier,
                                "raw_text": text.strip()[:500],
                            })
                            if len(shipments) >= count:
                                break
                    except Exception:
                        continue
                if len(shipments) >= count:
                    break
            except Exception as e:
                _log(verbose, f"  Skip selector {selector}: {e}")
            if len(shipments) >= count:
                break

        # Fallback: find all tracking numbers in page text, take first `count` unique
        if len(shipments) < count and html:
            _log(verbose, "Fallback: scanning page for tracking numbers...")
            for match in _TRACKING_PATTERN.finditer(html):
                tn = match.group(1)
                if tn in seen_tracking:
                    continue
                if len(tn) < 12:
                    continue
                seen_tracking.add(tn)
                carrier = "USPS" if tn.startswith("94") else ("UPS" if tn.startswith("1Z") else "Unknown")
                shipments.append({
                    "tracking_number": tn,
                    "carrier": carrier,
                    "raw_text": "",
                })
                if len(shipments) >= count:
                    break

        shipments = shipments[:count]
        _log(verbose, f"Done. Found {len(shipments)} shipment(s).")
        await browser.close()
        await p.stop()
        return {"success": True, "shipments": shipments, "url": url_used}
    except Exception as e:
        _log(verbose, f"ERROR: {e}")
        try:
            await browser.close()
            await p.stop()
        except Exception:
            pass
        return {"success": False, "shipments": [], "error": str(e)}


async def get_page_after_login(
    path: str = "/ship",
    email: Optional[str] = None,
    password: Optional[str] = None,
    headless: bool = True,
    verbose: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Log in and navigate to a path (e.g. /ship). Return page HTML and URL for custom scraping.
    Set verbose=True or PIRATESHIP_VERBOSE=1 for progress messages.
    """
    verbose = verbose if verbose is not None else _verbose_default()
    result = await login(email=email, password=password, headless=headless, verbose=verbose)
    if not result.get("success"):
        return {"success": False, "html": "", "url": "", "error": result.get("error")}

    page = result["page"]
    browser = result["browser"]
    p = result["playwright"]
    try:
        await page.goto(f"{PIRATESHIP_BASE}{path}", wait_until="domcontentloaded")
        await asyncio.sleep(0.1)
        html = await page.content()
        url = page.url
        await browser.close()
        await p.stop()
        return {"success": True, "html": html, "url": url}
    except Exception as e:
        try:
            await browser.close()
            await p.stop()
        except Exception:
            pass
        return {"success": False, "html": "", "url": "", "error": str(e)}


def run_async(coro):
    """Run an async function from sync code."""
    return asyncio.run(coro)


if __name__ == "__main__":
    # Examples:
    #   Report (requests):  python pirateship_scraper.py report 17-14149-65322
    #   Rates (Playwright): python pirateship_scraper.py rates 90210 10001 16
    import sys
    mode = (sys.argv[1] or "rates").lower() if len(sys.argv) > 1 else "rates"
    if mode == "report":
        ebay_order_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not ebay_order_id:
            print("Usage: python pirateship_scraper.py report <ebay_order_id>")
            sys.exit(2)
        result = get_shipment_report(ebay_order_id, verbose=True)
        print("--- result ---")
        if result.get("success"):
            print("URL:", result.get("url"))
            surl = result.get("shipment_url")
            if surl:
                print("Shipment URL:", surl)
            print("Has shipment span:", result.get("has_shipment_span", False))
            if result.get("shipment_span_text"):
                print("Shipment span text:", result.get("shipment_span_text")[:200])
            c = result.get("cost")
            if c is not None:
                print("Cost:", f"${c:.2f}")
        else:
            print("Error:", result.get("error"))
        sys.exit(0 if result.get("success") else 1)
    # rates: python pirateship_scraper.py [rates] <from_zip> <to_zip> <weight_oz>
    if mode == "rates":
        from_zip = sys.argv[2] if len(sys.argv) > 2 else "90210"
        to_zip = sys.argv[3] if len(sys.argv) > 3 else "10001"
        weight = float(sys.argv[4]) if len(sys.argv) > 4 else 16.0
    else:
        from_zip = sys.argv[1] if len(sys.argv) > 1 else "90210"
        to_zip = sys.argv[2] if len(sys.argv) > 2 else "10001"
        weight = float(sys.argv[3]) if len(sys.argv) > 3 else 16.0
    result = run_async(get_rates(from_zip, to_zip, weight, verbose=True))
    print("--- result ---")
    if result.get("success"):
        for r in result.get("rates", []):
            print(r.get("text", r)[:200])
    else:
        print("Error:", result.get("error"))
    sys.exit(0 if result.get("success") else 1)
