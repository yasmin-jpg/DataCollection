# scraper.py
import time
import pandas as pd
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import random

def scrape_data():
    # Определяем пути
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # src -> project root
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Путь для CSV файла
    csv_path = os.path.join(DATA_DIR, "dirty_data.csv")

    URLS_TO_SCRAPE = [
        "https://www2.hm.com/en_asia1/ladies.html",
        "https://www2.hm.com/en_asia1/ladies/shop-by-product/jeans.html",
        "https://www2.hm.com/en_asia1/ladies/shop-by-product/tops.html",
        "https://www2.hm.com/en_asia1/ladies/shop-by-product/dresses.html",
        "https://www2.hm.com/en_asia1/ladies/shop-by-product/skirts.html",
        "https://www2.hm.com/en_asia1/ladies/shop-by-product/trousers.html"
    ]

    temp_profile_path = os.path.join(os.getcwd(), f"chrome_profile_{int(time.time())}")
    
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--incognito") 
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-data-dir={temp_profile_path}") 
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => false
        });
        """
    })

    all_products = []
    target_count = 110

    try:
        for url in URLS_TO_SCRAPE:
            if len(all_products) >= target_count:
                break
                
            driver.get(url)
            time.sleep(random.uniform(8, 12))
            
            try:
                cookie_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
                cookie_btn.click()
                time.sleep(2)
            except:
                pass
                
            for i in range(5):
                driver.execute_script(f"window.scrollTo(0, {1000 * (i+1)});")
                time.sleep(random.uniform(2, 3))
            
            time.sleep(3)
            
            items = driver.find_elements(By.CSS_SELECTOR, 'article.d4725d')
            
            if not items:
                items = driver.find_elements(By.CSS_SELECTOR, 'article[data-articlecode]')
            
            if not items:
                items = driver.find_elements(By.CSS_SELECTOR, '[data-articlecode]')
            
            if not items:
                items = driver.find_elements(By.CSS_SELECTOR, '.d45665')
            
            count_on_page = 0
            for item in items[:50]:
                if len(all_products) >= target_count:
                    break
                    
                try:
                    title = ""
                    price = ""
                    brand = "H&M"
                    
                    try:
                        title_elem = item.find_element(By.CSS_SELECTOR, 'h2.b9e19c')
                        title = title_elem.text.strip()
                    except:
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, 'h2, h3, .b9e19c, .bldbab, .b4ec90')
                            title = title_elem.text.strip()
                        except:
                            pass
                    
                    try:
                        price_elem = item.find_element(By.CSS_SELECTOR, 'span.d16b8d')
                        price = price_elem.text.strip()
                    except:
                        try:
                            price_elems = item.find_elements(By.XPATH, './/span[contains(@class, "d16b8d") or contains(text(), "HK$") or contains(text(), "$")]')
                            for price_elem in price_elems:
                                price_text = price_elem.text.strip()
                                if price_text and ('HK$' in price_text or '$' in price_text):
                                    price = price_text
                                    break
                        except:
                            pass
                    
                    try:
                        brand_elem = item.find_element(By.CSS_SELECTOR, 'span.28888')
                        brand_text = brand_elem.text.strip()
                        if brand_text:
                            brand = brand_text
                    except:
                        pass
                    
                    if not title or not price:
                        item_text = item.text.strip()
                        lines = [line.strip() for line in item_text.split('\n') if line.strip()]
                        
                        if not title and lines:
                            candidate_titles = [line for line in lines if not any(c in line for c in ['$', 'HK$', '€']) and len(line) > 10]
                            if candidate_titles:
                                title = candidate_titles[0]
                        
                        if not price and lines:
                            for line in lines:
                                if 'HK$' in line or '$' in line:
                                    price = line
                                    break
                    
                    if title and price:
                        title = title.replace('\n', ' ').replace('\r', ' ').strip()
                        price = price.replace('\n', ' ').replace('\r', ' ').strip()
                        price = ' '.join(price.split())
                        
                        prod_obj = {
                            "brand": brand,
                            "description": title,
                            "price_raw": price
                        }
                        
                        is_duplicate = False
                        for existing in all_products:
                            if (existing["description"].lower() == prod_obj["description"].lower() or
                                (existing["price_raw"] == prod_obj["price_raw"] and 
                                 existing["description"][:20] == prod_obj["description"][:20])):
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            all_products.append(prod_obj)
                            count_on_page += 1
                            
                except:
                    continue
            
            time.sleep(random.uniform(3, 5))
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        try:
            driver.quit()
        except:
            pass
        
        try:
            shutil.rmtree(temp_profile_path, ignore_errors=True)
        except:
            pass
    
    df = pd.DataFrame(all_products)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['description', 'price_raw'], keep='first')
    removed_duplicates = initial_count - len(df)
    
    # Исправленный путь - используем os.path.join
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    print(f"Target: {target_count}")
    print(f"Collected: {len(df)}")
    print(f"Duplicates removed: {removed_duplicates}")
    print(f"Data saved to: {csv_path}")
    
    if len(df) > 0:
        print(f"Missing to target: {max(0, target_count - len(df))}")
        
    return df

if __name__ == "__main__":
    scrape_data()