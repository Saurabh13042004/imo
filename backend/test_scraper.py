import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = (
    "https://www.google.co.in/search?"
    "ibp=oshop&q=canon&"
    "prds=catalogid:16777480787845703300,"
    "headlineOfferDocid:6625633141554705753,"
    "imageDocid:16096869997558031535,"
    "rds:PC_14636930435103823651|PROD_PC_14636930435103823651,"
    "gpcid:14636930435103823651,"
    "mid:576462440853044345,pvt:hg&"
    "hl=en&gl=in&udm=28"
)

# ---------- CHROME SETUP (HEADLESS) ----------
options = Options()
options.add_argument("--headless=new")   # NEW headless (important)
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service()  # uses chromedriver from PATH

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

driver.get(URL)

# ---------- HELPERS ----------
def get_reviews():
    return driver.find_elements(By.CSS_SELECTOR, 'div[data-attrid="user_review"]')

def click_more_reviews():
    try:
        btn = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[role="button"][jsaction*="trigger.MS0zad"]')
        ))
        driver.execute_script("arguments[0].click();", btn)
        return True
    except:
        return False

def expand_all_reviews():
    buttons = driver.find_elements(
        By.CSS_SELECTOR,
        'div[jsaction*="trigger.nNRzZb"]'
    )
    for b in buttons:
        try:
            driver.execute_script("arguments[0].click();", b)
        except:
            pass

# ---------- LOAD REVIEWS (SMART STOP) ----------
last_count = 0
stable_rounds = 0
MAX_ROUNDS = 6   # usually finishes in 2–3

for i in range(MAX_ROUNDS):
    expand_all_reviews()
    time.sleep(1)

    reviews = get_reviews()
    count = len(reviews)
    print(f"[{i+1}] Reviews loaded: {count}")

    if count == last_count:
        stable_rounds += 1
    else:
        stable_rounds = 0

    if stable_rounds >= 2:
        print("Review count stabilized — stopping.")
        break

    last_count = count
    if not click_more_reviews():
        break

    time.sleep(1.5)

print(f"\n✅ Final review count: {len(get_reviews())}\n")

# ---------- PARSE DATA ----------
results = []

for r in get_reviews():
    def safe(css):
        try:
            return r.find_element(By.CSS_SELECTOR, css).text
        except:
            return ""

    results.append({
        "name": safe(".cbsD0d"),
        "rating": safe(".yi40Hd"),
        "review": safe(".v168Le"),
        "source": safe(".xuBzLd")
    })

# ---------- OUTPUT ----------
for i, r in enumerate(results[:5], 1):
    print(f"{i}. {r['name']} ({r['rating']}⭐)")
    print(r["review"][:140])
    print("Source:", r["source"])
    print("-" * 60)

driver.quit()
