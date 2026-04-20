"""In-memory cache for report POST results (e.g. profit). Must be cleared when underlying data changes."""
import hashlib
import json
from datetime import datetime

report_cache = {}
CACHE_DURATION = 300  # 5 minutes


def get_cache_key(report_type, params):
    param_str = json.dumps(params, sort_keys=True)
    return "{}_{}".format(report_type, hashlib.md5(param_str.encode()).hexdigest())


def get_cached_report(report_type, params):
    cache_key = get_cache_key(report_type, params)
    if cache_key in report_cache:
        timestamp, data = report_cache[cache_key]
        if datetime.now().timestamp() - timestamp < CACHE_DURATION:
            return data
        del report_cache[cache_key]
    return None


def cache_report(report_type, params, data):
    cache_key = get_cache_key(report_type, params)
    report_cache[cache_key] = (datetime.now().timestamp(), data)


def clear_report_cache():
    """Call after item/group/sale changes so profit and other cached reports stay accurate."""
    report_cache.clear()
