
import pandas as pd
import os
import re

def new_data():
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    input_path = os.path.join(DATA_DIR, "dirty_data.csv")
    output_path = os.path.join(DATA_DIR, "cleaned_data.csv")
    
    if not os.path.exists(input_path):
        print(f"Error: No file found at {input_path}")
        return

    df = pd.read_csv(input_path)

    df.drop_duplicates(inplace=True)
    df = df.dropna()

    def extract_price(price_str):
        if pd.isna(price_str):
            return None
        clean_str = re.sub(r"[^\d.]", "", str(price_str))
        try:
            return float(clean_str) if clean_str else None
        except ValueError:
            return None

    df['price'] = df['price_raw'].apply(extract_price)
    df = df.dropna(subset=['price'])
    
    df['brand'] = df['brand'].astype(str)
    df['description'] = df['description'].astype(str)
    
    df['brand'] = df['brand'].str.strip()
    df['description'] = df['description'].str.strip()
    
    df['brand'] = df['brand'].fillna('H&M')
    df['description'] = df['description'].fillna('No description')

    final_df = df[['brand', 'description', 'price']]

    final_df.to_csv(output_path, index=False)
    
    print(f"Cleaned {len(final_df)} records")
    print(f"Saved to: {output_path}")
    print(f"Data types: brand={final_df['brand'].dtype}, description={final_df['description'].dtype}, price={final_df['price'].dtype}")

if __name__ == "__main__":
    new_data()