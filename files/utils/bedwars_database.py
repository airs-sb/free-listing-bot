import sqlite3

def initialize_bedwars_database():
    conn = sqlite3.connect('bedwars_accounts.db')
    c = conn.cursor()

    # Create a table for the Bedwars account listings and stats if it doesn't already exist
    c.execute('''CREATE TABLE IF NOT EXISTS bedwars_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id TEXT,
                    price INTEGER,
                    ign TEXT,
                    api_key TEXT,
                    payment_method TEXT,
                    additional_info TEXT,
                    channel_id TEXT,
                    channel_name TEXT,
                    rank TEXT,  -- Added rank field
                    stars INTEGER,
                    wins INTEGER,
                    losses INTEGER,
                    kills INTEGER,
                    deaths INTEGER,
                    final_kills INTEGER,
                    final_deaths INTEGER,
                    beds_broken INTEGER,
                    beds_lost INTEGER,
                    games_played INTEGER
                )''')

    conn.commit()
    conn.close()

# Function to insert a Bedwars account listing with stats into the database, including rank
def insert_bedwars_account(owner_id, price, ign, api_key, payment_method, additional_info, channel_id, channel_name, stats):
    conn = sqlite3.connect('bedwars_accounts.db')
    c = conn.cursor()

    c.execute('''INSERT INTO bedwars_accounts 
                (owner_id, price, ign, api_key, payment_method, additional_info, channel_id, channel_name,
                rank, stars, wins, losses, kills, deaths, final_kills, final_deaths, beds_broken, beds_lost, games_played)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (owner_id, price, ign, api_key, payment_method, additional_info, channel_id, channel_name,
               stats['rank'], stats['stars'], stats['wins'], stats['losses'], stats['kills'], stats['deaths'], 
               stats['final_kills'], stats['final_deaths'], stats['beds_broken'], stats['beds_lost'], 
               stats['games_played']))

    conn.commit()
    conn.close()

# Function to fetch all Bedwars account listings from the database
def fetch_all_bedwars_accounts():
    conn = sqlite3.connect('bedwars_accounts.db')
    c = conn.cursor()

    c.execute("SELECT * FROM bedwars_accounts")
    accounts = c.fetchall()

    conn.close()
    return accounts

# Function to remove a Bedwars account from the database by channel_id
def remove_bedwars_account(channel_id: int):
    conn = sqlite3.connect('bedwars_accounts.db')
    c = conn.cursor()

    # Remove the account by channel ID
    c.execute("DELETE FROM bedwars_accounts WHERE channel_id = ?", (channel_id,))
    conn.commit()
    conn.close()
