import sqlite3
import os

def init_db():
    # Initialize database connection
    db_path = 'bots.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create table if not exists
    c.execute('''
    CREATE TABLE IF NOT EXISTS bots (
        bot_id TEXT, 
        folder TEXT, 
        main_file TEXT, 
        config TEXT
    )
    ''')

    c.execute('''

    CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    credits INTEGER DEFAULT 0
);

              
              
              
              ''')
    

    c.execute('''


    CREATE TABLE IF NOT EXISTS keys (
    key TEXT PRIMARY KEY,
    credits INTEGER,
    redeemed INTEGER DEFAULT 0
);
        
              
              
              
              ''')
    
    conn.commit()
    return conn, c


