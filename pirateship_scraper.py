"""
Pirate Ship scraper using Playwright.

Uses browser automation to log in and scrape/ interact with pirateship.com.
Credentials: set PIRATESHIP_EMAIL and PIRATESHIP_PASSWORD in environment,
or pass them to login().

Note: Scraping may violate Pirate Ship's Terms of Service. Prefer an official
API if available. Use responsibly and at your own risk.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List


# Base URL for Pirate Ship
PIRATESHIP_BASE = "https://www.pirateship.com"


async def _get_browser(headless: bool = True):
    """Launch Playwright browser. Install with: playwright install chromium"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError("Install playwright: pip install playwright && playwright install chromium")
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=headless)
    return p, browser


async def login(
    email: Optional[str] = None,
    password: Optional[str] = None,
    headless: bool = True,
) -> Dict[str, Any]:
    """
    Log in to Pirate Ship and return context (page, browser) for further actions.
    Email/password default to env PIRATESHIP_EMAIL, PIRATESHIP_PASSWORD.
    """
    email = email or os.environ.get("PIRATESHIP_EMAIL")
    password = password or os.environ.get("PIRATESHIP_PASSWORD")
    if not email or not password:
        return {"success": False, "error": "PIRATESHIP_EMAIL and PIRATESHIP_PASSWORD required"}

    p = None
    browser = None
    try:
        p, browser = await _get_browser(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(f"{PIRATESHIP_BASE}/login", wait_until="networkidle")
        await page.fill('input[name="email"], input[type="email"]', email)
        await page.fill('input[name="password"], input[type="password"]', password)
        await page.click('button[type="submit"], input[type="submit"], [data-testid="login-submit"]')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)

        # Check if we're on dashboard (logged in)
        url = page.url
        if "login" in url:
            return {"success": False, "error": "Login failed (still on login page)"}
        return {
            "success": True,
            "page": page,
            "context": context,
            "browser": browser,
            "playwright": p,
        }
    except Exception as e:
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
) -> Dict[str, Any]:
    """
    Log in, open the rate-check flow, fill origin/dest/weight (and dimensions if provided),
    then scrape the displayed rates.
    Returns { "success": bool, "rates": [...], "error": str }.
    """
    result = await login(email=email, password=password, headless=headless)
    if not result.get("success"):
        return {"success": False, "rates": [], "error": result.get("error", "Login failed")}

    page = result["page"]
    browser = result["browser"]
    p = result["playwright"]
    rates: List[Dict[str, Any]] = []

    try:
        # Navigate to create shipment / get rates (common paths)
        await page.goto(f"{PIRATESHIP_BASE}/ship", wait_until="networkidle")
        await asyncio.sleep(1.5)

        # Try to find and fill origin/destination/weight (selectors may need tuning for current site)
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

        # Trigger get rates (button or auto-submit)
        await page.click('button:has-text("Get rates"), button:has-text("Rates"), [data-testid="get-rates"]')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        # Scrape rate rows (adjust selectors to match current Pirate Ship markup)
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

        await browser.close()
        await p.stop()
        return {"success": True, "rates": rates}
    except Exception as e:
        try:
            await browser.close()
            await p.stop()
        except Exception:
            pass
        return {"success": False, "rates": [], "error": str(e)}


async def get_page_after_login(
    path: str = "/ship",
    email: Optional[str] = None,
    password: Optional[str] = None,
    headless: bool = True,
) -> Dict[str, Any]:
    """
    Log in and navigate to a path (e.g. /ship). Return page HTML and URL for custom scraping.
    """
    result = await login(email=email, password=password, headless=headless)
    if not result.get("success"):
        return {"success": False, "html": "", "url": "", "error": result.get("error")}

    page = result["page"]
    browser = result["browser"]
    p = result["playwright"]
    try:
        await page.goto(f"{PIRATESHIP_BASE}{path}", wait_until="networkidle")
        await asyncio.sleep(1)
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


# Example usage from sync code:
# from pirateship_scraper import get_rates, run_async
# result = run_async(get_rates("90210", "10001", 16.0))
