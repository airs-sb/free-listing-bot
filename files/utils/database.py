import sqlite3

def initialize_database():
    conn = sqlite3.connect('skyblock_accounts.db')
    c = conn.cursor()

    # Create a table for the account listings and stats if it doesn't already exist
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id TEXT,
                    price INTEGER,
                    ign TEXT,
                    api_key TEXT,
                    payment_method TEXT,
                    additional_info TEXT,
                    profile TEXT,
                    channel_id TEXT,
                    channel_name TEXT,
                    skill_average REAL,
                    catacombs_level REAL,
                    slayer_levels TEXT,
                    hotm_level INTEGER,
                    mithril_powder INTEGER,
                    gemstone_powder INTEGER,
                    networth_total TEXT,
                    networth_bank TEXT,
                    networth_purse TEXT,
                    networth_soulbound TEXT
                )''')

    conn.commit()
    conn.close()


# Function to insert an account listing with stats into the database
def insert_account(owner_id, price, ign, api_key, payment_method, additional_info, profile, channel_id, channel_name, stats):
    conn = sqlite3.connect('skyblock_accounts.db')
    c = conn.cursor()

    c.execute('''INSERT INTO accounts 
                (owner_id, price, ign, api_key, payment_method, additional_info, profile, channel_id, channel_name,
                skill_average, catacombs_level, slayer_levels, hotm_level, mithril_powder, gemstone_powder, networth_total, networth_bank, networth_purse, networth_soulbound)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (owner_id, price, ign, api_key, payment_method, additional_info, profile, channel_id, channel_name,
               stats['skill_average'], stats['catacombs_level'], stats['slayer_levels'], stats['hotm_level'], 
               stats['mithril_powder'], stats['gemstone_powder'], stats['networth_total'], stats['networth_bank'], 
               stats['networth_purse'], stats['networth_soulbound']))

    conn.commit()
    conn.close()

# Function to fetch all account listings from the database
def fetch_all_accounts():
    conn = sqlite3.connect('skyblock_accounts.db')
    c = conn.cursor()

    c.execute("SELECT * FROM accounts")
    accounts = c.fetchall()

    conn.close()
    return accounts

def remove_account(channel_id: int):
    conn = sqlite3.connect('skyblock_accounts.db')
    c = conn.cursor()

    # Remove the account by channel ID
    c.execute("DELETE FROM accounts WHERE channel_id = ?", (channel_id,))
    conn.commit()
    conn.close()


