"""Configuration for moderation action types and their properties."""

POINT_THRESHOLDS = {
    "TEMP_BAN": 50,
    "PERMANENT_BAN": 100,
    "DECAY_RATE": 5,  # points per month
    "DECAY_INTERVAL": 30  # days
}

VIOLATION_TYPES = {
    "SOLICITING_GIFTS": {
        "points": 10,
        "description": "Soliciting gifts from other players",
        "default_action": "warning"
    },
    "DISRESPECT_MINOR": {
        "points": 25,
        "description": "Minor disrespectful behavior",
        "default_action": "warning"
    },
    "DISRESPECT_MAJOR": {
        "points": 50,
        "description": "Major disrespectful behavior",
        "default_action": "warning"
    },
    "GROSS_DISRESPECT": {
        "points": 100,
        "description": "Gross disrespect or harassment",
        "default_action": "warning"
    },
    "ADVERTISING": {
        "points": 25,
        "description": "Unauthorized advertising",
        "default_action": "warning"
    },
    "TROLLING": {
        "points": 25,
        "description": "Trolling or disruptive behavior",
        "default_action": "warning"
    },
    "IMPERSONATION": {
        "points": 75,
        "description": "Impersonating officers or other members",
        "default_action": "warning"
    },
    "EXPLOITING": {
        "points": 50,
        "description": "Exploiting game mechanics",
        "default_action": "warning"
    }
}

MOD_ACTION_TYPES = {
    "warning": {
        "severity": 1,
        "blocks_access": False,
        "default_duration": None,
        "description": "Warning with potential point penalty",
        "color": "#FFA500",  # Orange
        "requires_points": True
    },
    "mute": {
        "severity": 2,
        "blocks_access": False,
        "default_duration": 24,  # hours
        "description": "Cannot use guild/discord chat",
        "color": "#FF6B6B",  # Light red
        "requires_points": False
    },
    "kick": {
        "severity": 3,
        "blocks_access": False,
        "default_duration": None,
        "description": "Removed from guild, can rejoin",
        "color": "#DC143C",  # Crimson
        "requires_points": False
    },
    "temp_ban": {
        "severity": 4,
        "blocks_access": True,
        "default_duration": 168,  # 1 week
        "description": "Temporary ban from all guild activities",
        "color": "#8B0000",  # Dark red
        "requires_points": False
    },
    "ban": {
        "severity": 5,
        "blocks_access": True,
        "default_duration": None,  # Permanent
        "description": "Permanent ban from all guild activities",
        "color": "#000000",  # Black
        "requires_points": False
    }
}

def get_action_type_info(action_type: str) -> dict:
    """Get information about a moderation action type."""
    return MOD_ACTION_TYPES.get(action_type, {
        "severity": 1,
        "blocks_access": False,
        "default_duration": None,
        "description": "Unknown action type",
        "color": "#808080",
        "requires_points": False
    })

def get_violation_info(violation_type: str) -> dict:
    """Get information about a violation type."""
    return VIOLATION_TYPES.get(violation_type, {
        "points": 0,
        "description": "Unknown violation type",
        "default_action": "warning"
    })

def is_blocking_action(action_type: str) -> bool:
    """Check if an action type blocks access."""
    info = get_action_type_info(action_type)
    return info.get("blocks_access", False)

def get_points_for_violation(violation_type: str) -> int:
    """Get the point value for a violation type."""
    info = get_violation_info(violation_type)
    return info.get("points", 0)

def should_auto_disable(current_points: int) -> bool:
    """Check if an account should be auto-disabled based on points."""
    return current_points >= POINT_THRESHOLDS["PERMANENT_BAN"]

def should_suggest_temp_ban(current_points: int) -> bool:
    """Check if a temporary ban should be suggested based on points."""
    return current_points >= POINT_THRESHOLDS["TEMP_BAN"] 