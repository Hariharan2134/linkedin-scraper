import sys
import time
import random
import re
import os
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# →→ GOOGLE SHEETS IMPORTS
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# ==========================================================
#          READ VALUES PASSED FROM DJANGO
# ==========================================================
QUERY = sys.argv[1] if len(sys.argv) > 1 else "UX Designer"
TOTAL_PAGES = int(sys.argv[2]) if len(sys.argv) > 2 else 1
MAX_PROFILES = int(sys.argv[3]) if len(sys.argv) > 3 else 10


# ==========================================================
#                 CONFIGS (UNCHANGED)
# ==========================================================
GOOGLE_SHEET_ID = "1gJlUnxq-wsUWsnDf1t8f2_fFgMb1yJlcG58nLwMG8vo"
SHEET_NAME = QUERY[:30]

USERNAME = "srihariharan213@gmail.com"        # Add your LinkedIn email here
PASSWORD = "Hariharan@213"       # Your LinkedIn password

MIN_DELAY = 1.0
MAX_DELAY = 2.5

EMAIL_REGEX = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}"
PHONE_PATTERNS = [
    r"\+91[-\s]?\d{10}",
    r"\b\d{10}\b",
    r"\+\d{1,3}[-\s]?\d{6,12}",
]


# ==========================================================
#                 UTIL FUNCTIONS
# ==========================================================
def rand_sleep():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def start_driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )
    wait = WebDriverWait(driver, 20)
    return driver, wait


def safe_find_click(driver, xpaths):
    for xp in xpaths:
        try:
            el = driver.find_element(By.XPATH, xp)
            driver.execute_script("arguments[0].click();", el)
            return True
        except:
            continue
    return False


def extract_from_modal_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    em = re.search(EMAIL_REGEX, text)
    email = em.group(0) if em else ""

    phone = ""
    for p in PHONE_PATTERNS:
        m = re.search(p, text)
        if m:
            phone = m.group(0)
            break

    return email, phone


# ==========================================================
#             GOOGLE SHEET HANDLING
# ==========================================================
def init_google_sheet():
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        r"C:\Users\sriha\Downloads\sheets-471808-c719e23b7ec2.json",
        scope
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID)

    try:
        ws = sheet.worksheet(SHEET_NAME)
    except:
        ws = sheet.add_worksheet(title=SHEET_NAME, rows="1000", cols="10")
        ws.append_row(["Name", "Email", "Phone", "Profile URL", "Page Number"])

    return ws


# ==========================================================
#                MAIN SCRAPER FUNCTION
# ==========================================================
def scrape():
    print("\n========== SCRAPER STARTED ==========")
    print(f"Query: {QUERY}")
    print(f"Pages: {TOTAL_PAGES}")
    print(f"Max Profiles Per Page: {MAX_PROFILES}\n")

    ws = init_google_sheet()
    existing_urls = ws.col_values(4)

    driver, wait = start_driver()

    try:
        # LOGIN
        print("Logging into LinkedIn...")
        driver.get("https://www.linkedin.com/login")

        wait.until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)

        print("Login success.\n")

        # LOOP THROUGH PAGES
        for user_page in range(1, TOTAL_PAGES + 1):

            print(f"\nScraping Page {user_page} of {TOTAL_PAGES}")

            profile_urls = []

            search_url = f"https://www.linkedin.com/search/results/people/?keywords={QUERY}&page={user_page}"
            driver.get(search_url)
            time.sleep(4)

            # scroll to load more profiles
            for _ in range(4):
                driver.execute_script("window.scrollBy(0, 900);")
                rand_sleep()

            cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/in/']")

            for a in cards:
                if len(profile_urls) >= MAX_PROFILES:
                    break

                href = (a.get_attribute("href") or "").split("?")[0]

                if "/in/" in href and href not in profile_urls:
                    profile_urls.append(href)

            print(f"Collected {len(profile_urls)} profiles.")

            # SCRAPE EACH PROFILE
            for idx, url in enumerate(profile_urls, start=1):

                if url in existing_urls:
                    print(f"Skipping duplicate: {url}")
                    continue

                print(f"[{idx}] Visiting: {url}")

                driver.get(url)
                time.sleep(3)

                try:
                    name = driver.find_element(By.TAG_NAME, "h1").text.strip()
                except:
                    name = "N/A"

                contact_xpaths = [
                    "//a[contains(@href,'contact-info')]",
                    "//button[contains(@aria-label,'Contact info')]",
                ]
                clicked = safe_find_click(driver, contact_xpaths)

                email, phone = "", ""

                if clicked:
                    time.sleep(2)
                    try:
                        modal = driver.find_element(By.CSS_SELECTOR, "div[role='dialog']")
                        html = modal.get_attribute("outerHTML")
                    except:
                        html = driver.page_source

                    email, phone = extract_from_modal_html(html)

                ws.append_row([name, email, phone, url, user_page])

                print(f"Saved: {name}, {email}, {phone}")

                rand_sleep()

        print("\nSCRAPING COMPLETED. Data stored in Google Sheets.")

    except Exception as e:
        print("\nERROR OCCURRED:")
        print(traceback.format_exc())

    finally:
        driver.quit()
        print("Browser closed.")


# ==========================================================
#                RUN WHEN EXECUTED
# ==========================================================
if __name__ == "__main__":
    scrape()
