"""API client for communicating with the C++ backend."""
import json
import time
from typing import Any, Dict, List, Tuple

import requests

from config import API_BASE_URL, REQUEST_TIMEOUT, REQUEST_TIMEOUT_POST, CACHE_TTL

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

    # API_BASE_URL is http://cpp_backend:8080/api
    # If endpoint already has /api prefix, don't add it again
    # Just pass endpoint as-is to be appended to base URL
    # For example: _get("/api/stats") -> http://cpp_backend:8080/api + /api/stats (WRONG)
    # We need to remove /api from endpoint: /api/stats -> /stats
    # Then: http://cpp_backend:8080/api + /stats = http://cpp_backend:8080/api/stats (CORRECT)
    if endpoint.startswith("/api/"):
        # Remove "/api" prefix, keep the slash: "/api/stats" -> "/stats"
        endpoint = endpoint[4:]
    elif endpoint.startswith("/api"):
        endpoint = endpoint[4:]  # Remove "/api" prefix: "/api" -> ""
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

    now = time.time()
    cached = _api_cache.get(endpoint)
    if cached and now - cached[0] <= CACHE_TTL:
        return cached[1]

    max_retries = 2
    last_error = None

    for attempt in range(max_retries):
        try:
            full_url = f"{API_BASE_URL}{endpoint}"
            try:
                from flask import current_app
                current_app.logger.info(f"API GET request: {full_url}")
            except:
                pass
            response = requests.get(full_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            try:
                from flask import current_app
                current_app.logger.info(f"API GET response: {data}")
            except:
                pass
            _api_cache[endpoint] = (now, data)
            return data
        except requests.ConnectionError as exc:
            last_error = f"Backend not available at {API_BASE_URL}"
            try:
                from flask import current_app
                current_app.logger.warning(
                    "API GET %s connection error (attempt %d/%d)", endpoint, attempt + 1, max_retries)
            except:
                pass
            if attempt < max_retries - 1:
                import time as time_module
                time_module.sleep(0.3)
                continue
        except requests.Timeout as exc:
            last_error = f"Timeout after {REQUEST_TIMEOUT}s"
            try:
                from flask import current_app
                current_app.logger.warning(
                    "API GET %s timeout (attempt %d/%d)", endpoint, attempt + 1, max_retries)
            except:
                pass
            if attempt < max_retries - 1:
                continue
        except requests.HTTPError as exc:
            try:
                from flask import current_app
                current_app.logger.warning(
                    "API GET %s HTTP %s", endpoint, exc.response.status_code)
            except:
                pass
            return default if default is not None else {}
        except requests.RequestException as exc:
            try:
                from flask import current_app
                current_app.logger.warning("API GET %s failed", endpoint)
            except:
                pass
            return default if default is not None else {}

    return default if default is not None else {}


def _post(endpoint: str, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Make a POST request to the API (no retry - backend is slow)."""
    # Ensure endpoint starts with /
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    # Remove /api prefix if present (API_BASE_URL already contains it)
    if endpoint.startswith("/api/"):
        endpoint = endpoint[4:]  # Remove "/api" prefix, keep the slash
    elif endpoint.startswith("/api"):
        endpoint = endpoint[4:]  # Remove "/api" prefix
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

    try:
        full_url = f"{API_BASE_URL}{endpoint}"
        try:
            from flask import current_app
            current_app.logger.info(f"API POST request: {full_url}")
        except:
            pass
        response = requests.post(
            full_url,
            json=payload,
            timeout=REQUEST_TIMEOUT_POST  # Use longer timeout for POST
        )
        response.raise_for_status()
        data = response.json()
        try:
            from flask import current_app
            current_app.logger.info(f"API POST response: {data}")
        except:
            pass
        return True, data
    except requests.ConnectionError as exc:
        error_msg = f"Backend server is not available at {API_BASE_URL}"
        try:
            from flask import current_app
            current_app.logger.error(
                "API POST %s connection error: %s", endpoint, exc)
        except:
            pass
        return False, {"status": "error", "message": error_msg}
    except requests.Timeout as exc:
        error_msg = f"Request timeout after {REQUEST_TIMEOUT_POST}s - backend is too slow"
        try:
            from flask import current_app
            current_app.logger.error("API POST %s timeout", endpoint)
        except:
            pass
        return False, {"status": "error", "message": error_msg}
    except requests.HTTPError as exc:
        try:
            from flask import current_app
            current_app.logger.error(
                "API POST %s HTTP error %s", endpoint, exc.response.status_code)
        except:
            pass
        return False, {"status": "error", "message": f"Server error: {exc.response.status_code}"}
    except requests.RequestException as exc:
        try:
            from flask import current_app
            current_app.logger.error("API POST %s failed", endpoint)
        except:
            pass
        return False, {"status": "error", "message": "Request failed"}


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
