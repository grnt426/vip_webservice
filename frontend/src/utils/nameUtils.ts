/**
 * Split a GW2 account name into display name and full name.
 * Example: "Nefretta.6810" -> { displayName: "Nefretta", fullName: "Nefretta.6810" }
 */
export function splitAccountName(accountName: string): { displayName: string; fullName: string } {
    if (!accountName) {
        return { displayName: "", fullName: "" };
    }

    const parts = accountName.split('.');
    if (parts.length > 1) {
        // Remove the last part (the numbers) and rejoin the rest
        // This handles names with dots in them like "dio di morte.7930"
        const displayName = parts.slice(0, -1).join('.');
        return { displayName, fullName: accountName };
    }
    return { displayName: accountName, fullName: accountName };
}

/**
 * Get the short version of a guild name.
 * Example: "Vengeance is Power" -> "Power"
 */
export function getShortGuildName(fullName: string): string {
    if (!fullName) {
        return "";
    }

    // Extract the last word from the guild name
    const words = fullName.split(' ');
    return words[words.length - 1] || fullName;
} 