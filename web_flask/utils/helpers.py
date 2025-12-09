"""Helper functions."""
import random
from typing import Any, Dict, List

from utils.teams import TEAM_LOOKUP
from utils.teams import _normalize


def get_team_by_name(name: str | None) -> Dict[str, Any] | None:
    """Get team by name from lookup."""
    if not name:
        return None
    return TEAM_LOOKUP.get(_normalize(name))


def build_roster(team: Dict[str, Any] | None, votes: Dict[int, int], side: str) -> List[Dict[str, Any]]:
    """Build roster with player positions on the pitch."""
    if not team:
        return []
    
    from utils.api_client import _get
    
    team_name = team.get("name")
    team_id = team.get("id")
    if not team_name and not team_id:
        return []
    
    # Load all players from API and filter by team_id
    players_data = _get("/players", default={"players": []}).get("players", [])
    if team_id:
        team_players = [p for p in players_data if p.get("team_id") == team_id]
    else:
        team_players = [p for p in players_data if _normalize(
            p.get("team_name", "")) == _normalize(team_name)]
    
    roster = []
    for player in team_players:
        player_id = player.get("id")
        player_name = player.get("name", "")
        position = player.get("position", "")
        
        # Default positions for players based on position code
        position_map = {
            "GK": {"x": 8, "y": 50},      # Goalkeeper - back center
            "CB": {"x": 15, "y": 50},     # Center Back - defense center
            "LB": {"x": 15, "y": 30},      # Left Back - defense left
            "RB": {"x": 15, "y": 70},      # Right Back - defense right
            # Center Midfielder - midfield center
            "CM": {"x": 35, "y": 50},
            "LM": {"x": 35, "y": 30},     # Left Midfielder - midfield left
            "RM": {"x": 35, "y": 70},      # Right Midfielder - midfield right
            "LW": {"x": 55, "y": 25},      # Left Winger - attack left
            "RW": {"x": 55, "y": 75},      # Right Winger - attack right
            "ST": {"x": 60, "y": 50},      # Striker - forward center
            "CF": {"x": 60, "y": 50},      # Center Forward - forward center
        }
        
        default_pos = position_map.get(position, {"x": 35, "y": 50})
        base_x = default_pos["x"]
        base_y = default_pos["y"]
        
        # Apply slight randomization to avoid overlapping players
        random.seed(player_id if player_id else hash(player_name))
        offset_x = random.uniform(-2, 2)
        offset_y = random.uniform(-3, 3)
        
        if side == "home":
            # Home team (Left side of pitch)
            x = max(5, min(48, base_x + offset_x))
            y = max(10, min(90, base_y + offset_y))
        else:
            # Away team (Right side of pitch)
            x = max(52, min(95, 100 - base_x - offset_x))
            y = max(10, min(90, 100 - base_y - offset_y))

        short_name = player_name.split()[-1] if player_name else ""
        number = short_name  # Use short_name instead of empty number

        roster.append({
            "name": player_name,
            "short_name": short_name,
            "number": number,
            "position": position,
            "x": x,
            "y": y,
            "player_id": player_id,
            "votes": votes.get(player_id, 0) if player_id else 0,
        })
    return roster

