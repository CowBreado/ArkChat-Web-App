import sqlite3
import os
import database
import random

backend_db_name = "practice"

#For the love of god, keep this to ensure that the generated database will only be in the same project folder, avoiding dupe .db files everywhere.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, f'{backend_db_name}.db')
connection = sqlite3.connect(DB_PATH)
print(f'Database connection established: {DB_PATH}')

#Cursor for actually handling queries using the connection object of sqlite3
cursor = connection.cursor()
#Create Table
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    age INTEGER NOT NULL               
)
""")



usernames = [
    "LunaFox", "IronMaple", "VelvetEcho", "ShadowWillow",
    "PixelHawk", "SilentTiger", "MossOtter", "CrimsonOak", "FrostRaven",
    "GoldenWisp", "NovaBerry", "AshenWolf", "CobaltFinch", "DustyPine",
    "EmberLynx", "FernShade", "GraniteCub", "HollowDeer", "IvyThorn",
    "JadeSparrow", "KestrelMoss", "LichenHart", "MapleVireo", "NimbusElk",
    "OnyxFawn", "PetalCrow", "QuartzMink", "RowanSnipe", "SableHeron",
    "ThistleFox", "UmberLark", "ViolaWren", "WillowTeal", "XenonHare",
    "YarrowGale", "ZephyrLoon", "AlderMink", "BirchOwl", "CedarVole",
]
database.open_db()
for username in usernames:
    password = "pass123"  # placeholder raw password, gets hashed inside create_user()
    age = random.randint(18, 35)
    database.create_user(username, password, age)


