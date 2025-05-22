def split_account_name(account_name: str) -> tuple[str, str]:
    """
    Split a GW2 account name into display name and account ID.
    Example: "Nefretta.6810" -> ("Nefretta", "Nefretta.6810")
    """
    if not account_name:
        return "", ""
    
    parts = account_name.split('.')
    if len(parts) > 1:
        # Remove the last part (the numbers) and rejoin the rest
        # This handles names with dots in them like "dio di morte.7930"
        display_name = '.'.join(parts[:-1])
        return display_name, account_name
    return account_name, account_name

def get_short_guild_name(full_name: str) -> str:
    """
    Get the short version of a guild name.
    Example: "Vengeance is Power" -> "Power"
    """
    if not full_name:
        return ""
    
    # Extract the last word from the guild name
    words = full_name.split()
    return words[-1] if words else full_name 