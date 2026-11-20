"""Shared helpers for RedTape Navigator scripts."""
import datetime
import json
import re
import sys

PENDING = "[PENDING_USER_INPUT]"

DOMAIN_DEFAULTS = {
    "business": {
        "food_prepared_on_site": None,
        "customer_seating": None,
        "commercial_lpg": None,
        "expected_annual_turnover_inr": None,
        "workers_on_site": None,
        "food_categories": None,
    },
    "zoning": {
        "plot_area_sqft": None,
        "proposed_floors": None,
        "current_land_use": None,
        "proposed_land_use": None,
        "road_width_ft": None,
        "heritage_or_eco_zone": None,
    },
    "agriculture": {
        "landholding_acres": None,
        "crop_types": None,
        "irrigation_source": None,
        "kisan_credit_card": None,
        "farmer_category": None,
        "bank_account_linked_aadhaar": None,
    },
    "general": {},
}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_path(data, dotted, default=None):
    cur = data
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def effective_value(state, dotted):
    """User overrides always win over agent-extracted values."""
    ov = state.get("overrides", {})
    if dotted in ov and ov[dotted] not in (None, ""):
        return ov[dotted]
    return get_path(state, dotted)


def is_blank(v):
    return v is None or (isinstance(v, str) and not v.strip()) or v == PENDING


def mask(v, keep=4):
    s = str(v)
    return "*" * max(0, len(s) - keep) + s[-keep:]


def inr_to_indian_words(amount):
    """Convert numeric INR to readable Indian scale words (e.g. 800000 -> '8 Lakhs')."""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return str(amount)
    if n >= 10_000_000:
        val = n / 10_000_000
        return f"Rs. {val:g} Crore"
    if n >= 100_000:
        val = n / 100_000
        return f"Rs. {val:g} Lakhs"
    if n >= 1_000:
        val = n / 1_000
        return f"Rs. {val:g} Thousand"
    return f"Rs. {int(n)}"


def apply_transform(value, name):
    if name is None or value is None:
        return value
    if name == "comma_list":
        if isinstance(value, list):
            return ", ".join(str(x) for x in value)
        return str(value)
    s = str(value).strip()
    if name == "upper":
        return s.upper()
    if name == "title":
        return s.title()
    if name == "digits":
        return re.sub(r"\D", "", s)
    if name == "phone_10digit":
        digits = re.sub(r"\D", "", s)
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        elif len(digits) == 11 and digits.startswith("0"):
            digits = digits[1:]
        return digits
    if name == "pan":
        return re.sub(r"\s+", "", s).upper()
    if name == "date_ddmmyyyy":
        try:
            return datetime.date.fromisoformat(s[:10]).strftime("%d/%m/%Y")
        except ValueError:
            return s
    if name == "inr_words":
        return inr_to_indian_words(value)
    raise ValueError(f"Unknown transform: {name}")


def need(module, pip_name):
    print(f"Missing dependency '{module}'. Install with: pip install {pip_name}", file=sys.stderr)
    sys.exit(2)
