import sqlite3
import os
from pprint import pprint

# Get the absolute path to the database file
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dumps', 'guild.db')

# Connect to the database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # This enables column access by name

# Query all guild ranks
cursor = conn.execute("""
    SELECT gr.*, g.name as guild_name, g.tag as guild_tag
    FROM guild_ranks gr
    JOIN guilds g ON gr.guild_id = g.id
    ORDER BY g.name, gr.order
""")

# Fetch and print all rows
rows = cursor.fetchall()
print("\nGuild Ranks:")
print("-" * 80)
for row in rows:
    print(f"\nGuild: {row['guild_name']} [{row['guild_tag']}]")
    print(f"Rank: {row['id']}")
    print(f"Order: {row['order']}")
    print(f"Permissions: {row['permissions']}")
    print("-" * 40)

conn.close() 