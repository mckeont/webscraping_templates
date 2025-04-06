import os
import time
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup
url = 'https://medbud.wiki/strains/'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get(url)

# Wait for the table to load
wait = WebDriverWait(driver, 15)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.product tbody tr')))
time.sleep(2)

# Scroll to bottom to load all content
previous_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.5)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == previous_height:
        break
    previous_height = new_height

# Create image output folder
image_folder = "medbud_images"
os.makedirs(image_folder, exist_ok=True)

# Extract data
rows = driver.find_elements(By.CSS_SELECTOR, 'table.product tbody tr')
data = []

for i, row in enumerate(rows):
    cols = row.find_elements(By.TAG_NAME, 'td')
    if len(cols) < 4:
        continue

    # Product name and strain name
    product_name = cols[1].text.strip().replace("\n", " ")
    strain_name = cols[3].text.strip().split("\n")[0]

    # Brand image
    brand_img_tag = cols[0].find_element(By.TAG_NAME, 'img') if cols[0].find_elements(By.TAG_NAME, 'img') else None
    brand_img_url = brand_img_tag.get_attribute('src') if brand_img_tag else ""

    # Strain image
    strain_img_tag = cols[3].find_element(By.TAG_NAME, 'img') if cols[3].find_elements(By.TAG_NAME, 'img') else None
    strain_img_url = strain_img_tag.get_attribute('src') if strain_img_tag else ""

    # Download brand image
    brand_filename = ""
    if brand_img_url:
        try:
            ext = brand_img_url.split('.')[-1].split('?')[0]
            brand_filename = f"brand_{i}.{ext}"
            response = requests.get(brand_img_url, timeout=10)
            with open(os.path.join(image_folder, brand_filename), 'wb') as f:
                f.write(response.content)
        except:
            brand_filename = ""

    # Download strain image
    strain_filename = ""
    if strain_img_url:
        try:
            ext = strain_img_url.split('.')[-1].split('?')[0]
            strain_filename = f"strain_{i}.{ext}"
            response = requests.get(strain_img_url, timeout=10)
            with open(os.path.join(image_folder, strain_filename), 'wb') as f:
                f.write(response.content)
        except:
            strain_filename = ""

    # Record data
    data.append({
        "Strain Name": strain_name,
        "Product Name": product_name,
        "Brand Image URL": brand_img_url,
        "Strain Image URL": strain_img_url,
        "Brand Image Filename": brand_filename,
        "Strain Image Filename": strain_filename
    })

driver.quit()

# Save to CSV
output_csv = "medbud_image_data.csv"
df = pd.DataFrame(data)
df.to_csv(output_csv, index=False)
print(f"✅ Data saved to {output_csv}")
