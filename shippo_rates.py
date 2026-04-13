"""
Shippo (goshippo.com) rate quotes — used by /api/shippo-rates.

Configure via Flask config or environment variables:
  SHIPPO_API_TOKEN       — API token from Shippo dashboard (test or live)
  SHIPPO_FROM_NAME       — Ship-from display name
  SHIPPO_FROM_STREET1    — Street line 1 (required for quotes)
  SHIPPO_FROM_STREET2    — Optional
  SHIPPO_FROM_CITY
  SHIPPO_FROM_STATE      — 2-letter state
  SHIPPO_FROM_ZIP
  SHIPPO_FROM_COUNTRY    — Default US
"""
import os
import re

import requests

SHIPPO_SHIPMENTS_URL = "https://api.goshippo.com/shipments/"
SHIPPO_API_VERSION = "2018-02-08"
ZIP_US_RE = re.compile(r"^\d{5}(-\d{4})?$")


def _cfg(app, key, env_key, default=""):
    return (app.config.get(key) if app else None) or os.environ.get(env_key, default)


def get_shippo_token(app):
    return (_cfg(app, "SHIPPO_API_TOKEN", "SHIPPO_API_TOKEN", "") or "").strip()


def get_address_from(app):
    """Build Shippo address_from dict from config/env."""
    country = (_cfg(app, "SHIPPO_FROM_COUNTRY", "SHIPPO_FROM_COUNTRY", "US") or "US").strip() or "US"
    return {
        "name": (_cfg(app, "SHIPPO_FROM_NAME", "SHIPPO_FROM_NAME", "Shipper") or "Shipper").strip(),
        "street1": (_cfg(app, "SHIPPO_FROM_STREET1", "SHIPPO_FROM_STREET1", "") or "").strip(),
        "street2": (_cfg(app, "SHIPPO_FROM_STREET2", "SHIPPO_FROM_STREET2", "") or "").strip() or None,
        "city": (_cfg(app, "SHIPPO_FROM_CITY", "SHIPPO_FROM_CITY", "") or "").strip(),
        "state": (_cfg(app, "SHIPPO_FROM_STATE", "SHIPPO_FROM_STATE", "") or "").strip(),
        "zip": (_cfg(app, "SHIPPO_FROM_ZIP", "SHIPPO_FROM_ZIP", "") or "").strip(),
        "country": country,
    }


def is_shippo_configured(app):
    """True when token and minimal ship-from address are set."""
    if not get_shippo_token(app):
        return False
    af = get_address_from(app)
    if not af.get("street1") or not af.get("zip"):
        return False
    if not af.get("city") or not af.get("state"):
        return False
    return True


def _float_or_default(val, default):
    try:
        if val is None or str(val).strip() == "":
            return default
        return float(val)
    except (TypeError, ValueError):
        return default


def _optional_float(val):
    """None if missing/blank; otherwise parse float."""
    try:
        if val is None or str(val).strip() == "":
            return None
        return float(val)
    except (TypeError, ValueError):
        return None


def build_address_to(body):
    """Validate and build address_to from JSON body."""
    zip_code = (body.get("to_zip") or "").strip()
    if not zip_code or not ZIP_US_RE.match(zip_code):
        raise ValueError("Valid US ZIP code is required (5 digits or ZIP+4).")
    street1 = (body.get("to_street1") or "").strip() or "General Delivery"
    city = (body.get("to_city") or "").strip() or "Unknown"
    state = (body.get("to_state") or "").strip().upper()
    if len(state) != 2:
        raise ValueError("Recipient state must be a 2-letter code (e.g. CA).")
    name = (body.get("to_name") or "").strip() or "Recipient"
    country = (body.get("to_country") or "US").strip() or "US"
    return {
        "name": name[:80],
        "street1": street1[:100],
        "city": city[:80],
        "state": state,
        "zip": zip_code[:10],
        "country": country[:2],
    }


def build_parcel(body):
    lb = _optional_float(body.get("weight_lb"))
    oz = _optional_float(body.get("weight_oz"))
    if lb is None and oz is None:
        weight = 1.0
    else:
        weight = (lb or 0.0) + (oz or 0.0) / 16.0
    if weight <= 0:
        raise ValueError("Weight must be greater than 0 (pounds and/or ounces).")
    if weight > 150:
        raise ValueError("Combined weight must not exceed 150 lb.")
    length = _float_or_default(body.get("length_in"), 12.0)
    width = _float_or_default(body.get("width_in"), 9.0)
    height = _float_or_default(body.get("height_in"), 3.0)
    for label, v in (("Length", length), ("Width", width), ("Height", height)):
        if v <= 0 or v > 108:
            raise ValueError("{} must be between 0 and 108 inches.".format(label))
    return {
        "length": str(round(length, 2)),
        "width": str(round(width, 2)),
        "height": str(round(height, 2)),
        "distance_unit": "in",
        "weight": str(round(weight, 2)),
        "mass_unit": "lb",
    }


def request_shipment_rates(token, address_from, address_to, parcel):
    """POST /shipments/ with async=false; return parsed JSON or raise."""
    # Do not set carrier_accounts: if present, Shippo only returns those IDs.
    # Omitting it polls every active carrier on the Shippo account (USPS, UPS, FedEx, etc.).
    payload = {
        "address_from": {k: v for k, v in address_from.items() if v is not None},
        "address_to": address_to,
        "parcels": [parcel],
        "async": False,
    }
    headers = {
        "Authorization": "ShippoToken {}".format(token),
        "Content-Type": "application/json",
        "SHIPPO-API-VERSION": SHIPPO_API_VERSION,
    }
    resp = requests.post(SHIPPO_SHIPMENTS_URL, json=payload, headers=headers, timeout=60)
    try:
        data = resp.json()
    except Exception:
        data = {}
    if resp.status_code >= 400:
        msg = data.get("detail") or data.get("__all__")
        if not msg and isinstance(data, dict):
            msg = data.get("non_field_errors") or str(data)
        if not msg:
            msg = resp.text[:500] or "Shippo API error {}".format(resp.status_code)
        raise ValueError(msg if isinstance(msg, str) else str(msg))
    return data


def normalize_rates(shipment_json):
    """Flatten Shippo rates for the UI, cheapest first."""
    raw = shipment_json.get("rates") or []
    out = []
    for r in raw:
        if not isinstance(r, dict):
            continue
        sl = r.get("servicelevel") or {}
        if isinstance(sl, dict):
            service = sl.get("name") or sl.get("token") or ""
        else:
            service = str(sl or "")
        try:
            amt = float(r.get("amount") or 0)
        except (TypeError, ValueError):
            amt = 0.0
        out.append(
            {
                "amount": r.get("amount"),
                "amount_float": amt,
                "currency": r.get("currency") or "USD",
                "provider": r.get("provider") or "",
                "service": service,
                "estimated_days": r.get("estimated_days"),
                "duration_terms": r.get("duration_terms") or "",
            }
        )
    out.sort(key=lambda x: x["amount_float"])
    return out
