"""Configuration for moderation action types and their properties."""

MOD_ACTION_TYPES = {
    "warning": {
        "severity": 1,
        "blocks_access": False,
        "default_duration": None,
        "description": "Formal warning, no access restrictions",
        "color": "#FFA500"  # Orange
    },
    "mute": {
        "severity": 2,
        "blocks_access": False,
        "default_duration": 24,  # hours
        "description": "Cannot use guild/discord chat",
        "color": "#FF6B6B"  # Light red
    },
    "kick": {
        "severity": 3,
        "blocks_access": False,
        "default_duration": None,
        "description": "Removed from guild, can rejoin",
        "color": "#DC143C"  # Crimson
    },
    "temp_ban": {
        "severity": 4,
        "blocks_access": True,
        "default_duration": 168,  # 1 week
        "description": "Temporary ban from all guild activities",
        "color": "#8B0000"  # Dark red
    },
    "ban": {
        "severity": 5,
        "blocks_access": True,
        "default_duration": None,  # Permanent
        "description": "Permanent ban from all guild activities",
        "color": "#000000"  # Black
    }
}

def get_action_type_info(action_type: str) -> dict:
    """Get information about a moderation action type."""
    return MOD_ACTION_TYPES.get(action_type, {
        "severity": 1,
        "blocks_access": False,
        "default_duration": None,
        "description": "Unknown action type",
        "color": "#808080"
    })

def is_blocking_action(action_type: str) -> bool:
    """Check if an action type blocks access."""
    info = get_action_type_info(action_type)
    return info.get("blocks_access", False) 