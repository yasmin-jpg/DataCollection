
import sqlite3
import pandas as pd
import os

def load_data():
   
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    input_path = os.path.join(DATA_DIR, "cleaned_data.csv")
    db_path = os.path.join(DATA_DIR, "hm_data.db")
    
    if not os.path.exists(input_path):
        print(f"Error: No file found at {input_path}")
        return

    df = pd.read_csv(input_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hm_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT,
        description TEXT,
        price REAL,
        loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    df.to_sql('hm_products', conn, if_exists='replace', index=False)
    
    print(f"Loaded {len(df)} rows into 'hm_products' table in {db_path}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    load_data()