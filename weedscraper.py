from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Setup Selenium
options = Options()
options.add_argument("--headless")  # Comment this out to watch it run
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

data = []
failed_pages = []

# Function to scrape one page
def scrape_page(page):
    url = f"https://www.weed.de/apothekensuche?page={page}"
    print(f"🌿 Scraping {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.w-full.rounded-3xl"))
        )
    except:
        print(f"⚠️ Timeout: No cards found on page {page}")
        failed_pages.append(page)
        return

    cards = driver.find_elements(By.CSS_SELECTOR, "li.w-full.rounded-3xl")
    print(f"✅ Found {len(cards)} pharmacy cards on page {page}")

    for card in cards:
        try:
            # Get pharmacy name (now fixed)
            try:
                name = card.find_element(By.CSS_SELECTOR, "p.font-semibold").text.strip()
            except:
                name = "N/A"

            # Get address
            try:
                address = card.find_element(By.XPATH, ".//p[contains(text(), ',')]").text.strip()
            except:
                address = "N/A"

            # Prices availability
            prices = "Yes" if "Prices available" in card.text else "No"

            # Get rating
            try:
                rating = card.find_element(By.CSS_SELECTOR, '[aria-label*="stars"]').get_attribute("aria-label")
            except:
                rating = "N/A"

            # Get profile link
            try:
                profile_link = card.find_element(By.XPATH, ".//a[contains(@href, '/apotheke/')]").get_attribute("href")
            except:
                profile_link = "Not available (not a partner)"

            data.append({
                "Name": name,
                "Address": address,
                "Prices Available": prices,
                "Rating": rating,
                "Profile Link": profile_link
            })

        except Exception as e:
            print("⛔ Skipping one pharmacy:", e)

# Loop through all 22 pages
for page in range(1, 23):
    scrape_page(page)

# Retry failed pages if needed
if failed_pages:
    print("🔁 Retrying failed pages...")
    for page in failed_pages:
        scrape_page(page)

# Save results
df = pd.DataFrame(data)
df.to_csv("weed_de_pharmacies.csv", index=False)
print(f"✅ Final save complete. {len(df)} pharmacies scraped and saved to weed_de_pharmacies.csv")

driver.quit()
