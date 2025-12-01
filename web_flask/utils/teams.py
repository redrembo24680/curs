"""Team-related utilities."""
from typing import Any, Dict

from utils.api_client import _get

# Teams data will be loaded from API (SQLite) instead of JSON
TEAMS_DATA: list[Dict[str, Any]] = []
TEAM_BY_SLUG: Dict[str, Dict[str, Any]] = {}
TEAM_LOOKUP: Dict[str, Dict[str, Any]] = {}


def _normalize(value: str) -> str:
    """Normalize string for lookup."""
    return "".join(ch for ch in value.lower() if ch.isalnum())


def _load_teams_from_api():
    """Load teams data from C++ backend API (SQLite) instead of JSON."""
    global TEAMS_DATA, TEAM_BY_SLUG, TEAM_LOOKUP
    try:
        api_response = _get("/teams", default={"teams": []})
        teams = api_response.get("teams", [])

        # Convert API format to expected format
        TEAMS_DATA = []
        for team in teams:
            team_dict = {
                "id": team.get("id"),
                "name": team.get("name", ""),
                "slug": _normalize(team.get("name", "")),
                "players": []  # Players will be loaded separately
            }
            TEAMS_DATA.append(team_dict)

        # Rebuild lookup dictionaries
        TEAM_BY_SLUG = {team["slug"]: team for team in TEAMS_DATA}
        TEAM_LOOKUP = {_normalize(team["name"]): team for team in TEAMS_DATA}

        try:
            from flask import current_app
            current_app.logger.info(f"Loaded {len(TEAMS_DATA)} teams from API (SQLite)")
        except:
            pass
        return True
    except Exception as e:
        try:
            from flask import current_app
            current_app.logger.error(f"Failed to load teams from API: {e}")
        except:
            pass
        return False


def sync_teams_and_players():
    """Sync teams and players from API (SQLite) - ensure all data is in sync."""
    # 1. Get teams from API (SQLite)
    api_teams = _get("/teams", default={"teams": []}).get("teams", [])
    
    # Reload teams from API to keep in sync
    _load_teams_from_api()

    # 2. Get players from API (SQLite)
    players_data = _get("/players", default={"players": []}).get("players", [])
    if not isinstance(players_data, list):
        players = []
    else:
        players = players_data

    try:
        from flask import current_app
        current_app.logger.info(
            f"Synced {len(api_teams)} teams and {len(players)} players from API (SQLite)")
    except:
        pass

