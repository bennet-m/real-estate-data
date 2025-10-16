import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10) 

driver.get("https://hpdonline.nyc.gov/hpdonline/building/314419/overview")
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.p-card-content")))
time.sleep(2)

# Scrape data
violations = {
    "A": int(driver.find_element(By.XPATH, "//span[contains(normalize-space(.),'A Class')]/span[@class='fw-bold']").text),
    "B": int(driver.find_element(By.XPATH, "//span[contains(normalize-space(.),'B Class')]/span[@class='fw-bold']").text),
    "C": int(driver.find_element(By.XPATH, "//span[contains(normalize-space(.),'C Class')]/span[@class='fw-bold']").text),
    "I": int(driver.find_element(By.XPATH, "//span[contains(normalize-space(.),'I Class')]/span[@class='fw-bold']").text),
}

stories = driver.find_element(
    By.XPATH, "//div[contains(@class,'card-content')][.//div[text()='STOREYS']]//div[contains(@class,'card-content-botttom')]"
).text.strip()

a_units = driver.find_element(
    By.XPATH, "//div[contains(@class,'card-content')][.//div[text()='A UNITS']]//div[contains(@class,'card-content-botttom')]"
).text.strip()

b_units = driver.find_element(
    By.XPATH, "//div[contains(@class,'card-content')][.//div[text()='B UNITS']]//div[contains(@class,'card-content-botttom')]"
).text.strip()

litigation_number = driver.find_element(
    By.CSS_SELECTOR, "span.fs-base > span.fw-bold"
).text.strip()

aep_status = driver.find_element(
    By.XPATH,
    "//span[text()='Alternate Enforcement Program (AEP)']/../../../../div[contains(@class,'content-right')]//span"
).text.strip()

conh_status = driver.find_element(
    By.XPATH,
    "//span[text()='Certification of No Harassment Pilot Program']/../../../../div[contains(@class,'content-right')]//span"
).text.strip()

driver.quit()

# Combine all data into a dictionary for pandas
data = {
    "Stories": stories,
    "A Units": a_units,
    "B Units": b_units,
    "Litigation": litigation_number,
    "AEP Status": aep_status,
    "CONH Status": conh_status,
    "A Violations": violations["A"],
    "B Violations": violations["B"],
    "C Violations": violations["C"],
    "I Violations": violations["I"],
}

# Create a DataFrame and export to CSV
df = pd.DataFrame([data])
df.to_csv("building_data.csv", index=False)
print("Data saved to building_data.csv")