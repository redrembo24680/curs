"""API client for communicating with the C++ backend."""
import json
import time
from typing import Any, Dict, List, Tuple

import requests

from config import API_BASE_URL, REQUEST_TIMEOUT, CACHE_TTL

# Global API cache
_api_cache: Dict[str, Tuple[float, Any]] = {}

# Global stats cache
_global_stats_cache: Tuple[float, Dict[str, Any]] | None = None
STATS_CACHE_TTL = 10.0


def _get(endpoint: str, default: Dict[str, Any] | List[Any] | None = None) -> Any:
    """Make a GET request to the API with caching."""
    # Ensure endpoint starts with /
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    # API_BASE_URL already includes /api, so we should NOT add /api prefix
    # Only normalize the endpoint path
    if endpoint.startswith("/api/"):
        endpoint = endpoint[4:]  # Remove /api prefix
    elif endpoint.startswith("/api"):
        endpoint = endpoint[4:]  # Remove /api prefix

    if endpoint in ["/", ""]:
        endpoint = "/"
    elif not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    now = time.time()
    cached = _api_cache.get(endpoint)
    if cached and now - cached[0] <= CACHE_TTL:
        return cached[1]

    try:
        full_url = f"{API_BASE_URL}{endpoint}"
        try:
            from flask import current_app
            current_app.logger.debug(f"API GET: {full_url}")
        except:
            pass  # No Flask context, skip logging
        response = requests.get(full_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        _api_cache[endpoint] = (now, data)
        try:
            from flask import current_app
            current_app.logger.debug(
                f"API GET {endpoint} returned {len(str(data))} bytes")
        except:
            pass  # No Flask context, skip logging
        return data
    except requests.ConnectionError as exc:
        try:
            from flask import current_app
            current_app.logger.error("API GET %s connection error: %s. Is backend running at %s?",
                                     endpoint, exc, API_BASE_URL)
        except:
            pass
        return default if default is not None else {}
    except requests.Timeout as exc:
        try:
            from flask import current_app
            current_app.logger.error("API GET %s timeout: %s", endpoint, exc)
        except:
            pass
        return default if default is not None else {}
    except requests.RequestException as exc:
        try:
            from flask import current_app
            current_app.logger.error("API GET %s failed: %s (type: %s)",
                                     endpoint, exc, type(exc).__name__)
        except:
            pass
        return default if default is not None else {}


def _post(endpoint: str, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Make a POST request to the API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return True, response.json()
    except requests.ConnectionError as exc:
        error_msg = f"Backend server is not available at {API_BASE_URL}. Please ensure the C++ server is running."
        try:
            from flask import current_app
            current_app.logger.error(
                "API POST %s connection error: %s", endpoint, exc)
        except:
            pass
        return False, {"status": "error", "message": error_msg}
    except requests.Timeout as exc:
        try:
            from flask import current_app
            current_app.logger.error("API POST %s timeout: %s", endpoint, exc)
        except:
            pass
        return False, {"status": "error", "message": f"Request timeout: {exc}"}
    except requests.RequestException as exc:
        try:
            from flask import current_app
            current_app.logger.error("API POST %s failed: %s (type: %s)",
                                     endpoint, exc, type(exc).__name__)
        except:
            pass
        return False, {"status": "error", "message": str(exc)}


def _invalidate_cache(*endpoints: str) -> None:
    """Invalidate cache for specified endpoints."""
    for ep in endpoints:
        _api_cache.pop(ep, None)


def get_cached_stats():
    """Get cached stats or fetch new ones."""
    global _global_stats_cache
    now = time.time()

    if _global_stats_cache and now - _global_stats_cache[0] <= STATS_CACHE_TTL:
        return _global_stats_cache[1]

    try:
        stats = _get(
            "/stats", default={"total_players": 0, "total_matches": 0, "total_votes": 0})
        _global_stats_cache = (now, stats)
        return stats
    except Exception as e:
        try:
            from flask import current_app
            current_app.logger.error(f"Error getting stats: {e}")
        except:
            pass
        return {"total_players": 0, "total_matches": 0, "total_votes": 0}
