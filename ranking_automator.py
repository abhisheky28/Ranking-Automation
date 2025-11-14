# ranking_automator.py (CORRECTED - With Advanced Detours and CAPTCHA Handling)

import time
import random
import logging
import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
import traceback
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

# --- These imports are unchanged, as they are required to read your existing config files ---
import config
import serp_selectors

# --- CONFIGURATION ---
AUTOMATOR_WORKSHEET_NAME = "Ranking Automator"
MAX_PAGES_TO_SCRAPE = 10

# --- NEW: LOCAL CONSTANTS FOR DETOURS (To avoid changing other files) ---
# The probability (0.0 to 1.0) of performing a detour. 0.50 = 50% chance.
DETOUR_PROBABILITY = 0.10

# All selectors for detouring are defined here locally.
DETOUR_SELECTORS = {
    "images": "a[href*='&tbm=isch']",
    "videos": "a[href*='&tbm=vid']",
    "news": "a[href*='&tbm=nws']",
    "maps": "a[href*='maps.google.com']"
}

# --- FIX #1: The missing SEARCH_INPUT selector is now defined locally here ---
SEARCH_INPUT_SELECTOR = "[name='q']"


# --- UPDATED: SLIGHTLY INCREASED DELAY CONFIGURATION ---
DELAY_CONFIG = {
    "typing": {"min": 0.01, "max": 0.01},
    "after_page_load": {"min": 0.01, "max": 0.01},
    "serp_read": {"min": 0.01, "max": 0.01},
    "before_next_page": {"min": 0.01, "max": 0.01},
    "between_keywords": {"min": 0.01, "max": 0.01},
    "detour_view": {"min": 0.01, "max": 0.01} # How long to "view" a detour page
}

# --- LOGGING & EMAIL FUNCTIONS ---
log_file_path = os.path.join(config.PROJECT_ROOT, 'ranking_automator.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(log_file_path, mode='w'), logging.StreamHandler()])
def send_error_email(subject, body):
    if not config.ENABLE_EMAIL_NOTIFICATIONS: return
    # --- FIX #2: Corrected the typo from RECIENT_EMAIL to RECIPIENT_EMAIL ---
    recipients = config.RECIPIENT_EMAIL
    logging.info(f"Preparing to send error email to: {', '.join(recipients)}")
    try:
        msg = MIMEText(body, 'plain')
        msg['Subject'], msg['From'], msg['To'] = subject, config.SENDER_EMAIL, ", ".join(recipients)
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
            server.sendmail(config.SENDER_EMAIL, recipients, msg.as_string())
            logging.info("Error email sent successfully.")
    except Exception as e:
        logging.error(f"CRITICAL: FAILED TO SEND ERROR EMAIL. Error: {e}")

# --- CAPTCHA HANDLING FUNCTION (No changes needed here) ---
def handle_captcha(driver, keyword):
    alert_sent = False
    start_time = time.time()
    logging.warning("!!! CAPTCHA DETECTED !!! Pausing script and waiting for manual intervention.")
    
    while time.time() - start_time < config.CAPTCHA_WAIT_TIMEOUT:
        captcha_elements = driver.find_elements(By.CSS_SELECTOR, 'iframe[title="reCAPTCHA"]')
        if not captcha_elements:
            logging.info("CAPTCHA solved! Resuming script.")
            return True

        if not alert_sent:
            print("\n" + "="*60)
            print(f"ACTION REQUIRED: Please solve the CAPTCHA in the browser.")
            print(f"The script will wait for up to {config.CAPTCHA_WAIT_TIMEOUT / 60:.0f} minutes.")
            print("It will automatically resume once the CAPTCHA is solved.")
            print("="*60 + "\n")
            
            email_subject = "Ranking Automator Alert: CAPTCHA - Action Required"
            email_body = f"Hello,\n\nThe script has encountered a Google CAPTCHA and is now paused.\n\nKeyword: \"{keyword}\"\n\nPlease solve the security check in the browser. The script will automatically resume.\n\n- Automated System"
            send_error_email(email_subject, email_body)
            alert_sent = True
        
        time.sleep(config.CAPTCHA_CHECK_INTERVAL)
        print(".", end="", flush=True)

    logging.error(f"CAPTCHA Timeout! Waited for {config.CAPTCHA_WAIT_TIMEOUT} seconds but CAPTCHA was not solved.")
    logging.error(f"Aborting keyword '{keyword}' and moving to the next one.")
    return False

# --- EXPANDED DETOUR FUNCTION (No changes needed here) ---
def perform_random_detour(driver, target_url):
    logging.info(">>> Performing a random detour for human-like behavior...")
    
    detour_options = list(DETOUR_SELECTORS.keys()) + ['random_link']
    chosen_detour = random.choice(detour_options)

    try:
        if chosen_detour == 'random_link':
            logging.info(f"...Detour: Clicking a random organic link.")
            all_results = driver.find_elements(By.CSS_SELECTOR, serp_selectors.RESULT_CONTAINER)
            non_target_links = []
            for result in all_results:
                try:
                    link_element = result.find_element(By.CSS_SELECTOR, serp_selectors.LINK_CONTAINER)
                    href = link_element.get_attribute('href')
                    if href and href.startswith('http') and target_url not in href:
                        non_target_links.append(link_element)
                except NoSuchElementException:
                    continue
            
            if non_target_links:
                random.choice(non_target_links).click()
            else:
                logging.warning("...Could not find a non-target link for detour, skipping.")
                return
        else:
            logging.info(f"...Detour: Clicking on '{chosen_detour.capitalize()}' tab.")
            selector = DETOUR_SELECTORS[chosen_detour]
            driver.find_element(By.CSS_SELECTOR, selector).click()

        time.sleep(random.uniform(DELAY_CONFIG["detour_view"]["min"], DELAY_CONFIG["detour_view"]["max"]))
        logging.info("<<< Returning from detour.")
        driver.back()
        time.sleep(random.uniform(2.0, 4.0))

    except (NoSuchElementException, ElementClickInterceptedException):
        logging.warning(f"Could not perform detour '{chosen_detour}'. The tab or link might not be available for this search.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during detour: {e}")


# --- HELPER & SETUP FUNCTIONS ---
def human_like_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(DELAY_CONFIG["typing"]["min"], DELAY_CONFIG["typing"]["max"]))

def find_and_type_in_search_box(driver, text):
    try:
        # --- FIX #1 (continued): Now using the local SEARCH_INPUT_SELECTOR instead of the one from serp_selectors ---
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, SEARCH_INPUT_SELECTOR)))
        search_box.clear()
        human_like_typing(search_box, text)
        search_box.send_keys(Keys.RETURN)
        return True
    except TimeoutException:
        logging.error("Could not find the search box. Cannot perform search.")
        return False
def get_humanlike_driver():
    logging.info("Initializing human-like Chrome WebDriver...")
    options = Options()
    random_user_agent = random.choice(config.USER_AGENTS)
    logging.info(f"Using User-Agent: {random_user_agent}")
    options.add_argument(f'user-agent={random_user_agent}')
    options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
    options.add_argument("--no-first-run"); options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions"); options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver

def connect_to_google_sheets():
    logging.info("Connecting to Google Sheets API...")
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(config.GCP_CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds); logging.info("Successfully connected to Google Sheets API.")
    return client

def get_data_from_sheet(worksheet):
    logging.info(f"Fetching data from worksheet: '{worksheet.title}'")
    records = worksheet.get_all_records(); df = pd.DataFrame(records)
    df['original_index'] = df.index + 2
    logging.info(f"Successfully fetched {len(df)} keywords.")
    return df

def find_rank_and_url(driver, target_url, rank_offset=0):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, serp_selectors.RESULT_CONTAINER)))
        all_potential_blocks = driver.find_elements(By.CSS_SELECTOR, serp_selectors.RESULT_CONTAINER)
        clean_organic_results = []
        for block in all_potential_blocks:
            try:
                if block.find_elements(By.CSS_SELECTOR, "[data-text-ad]"): continue
                h3_element = block.find_element(By.CSS_SELECTOR, "h3")
                if not h3_element.text.strip(): continue
                clean_organic_results.append(block)
            except NoSuchElementException: continue
        for rank, organic_block in enumerate(clean_organic_results, start=1 + rank_offset):
            try:
                link_element = organic_block.find_element(By.CSS_SELECTOR, serp_selectors.LINK_CONTAINER)
                actual_url = link_element.get_attribute('href')
                if not actual_url: continue
                if target_url in actual_url:
                    logging.info(f"SUCCESS: Found a match for '{target_url}'")
                    return rank, actual_url
            except NoSuchElementException: continue
    except Exception as e:
        logging.error(f"An error occurred during scraping on this page: {e}")
    return "Not Found", ""

# --- MAIN EXECUTION BLOCK (No changes needed here) ---
if __name__ == "__main__":
  #  logging.info("Attempting to terminate any running Chrome processes...")
 #   os.system("taskkill /F /IM chrome.exe >nul 2>&1")
    time.sleep(3)
    logging.info(f"--- Starting Ranking Automator Script for worksheet '{AUTOMATOR_WORKSHEET_NAME}' ---")
    driver = None
    try:
        gspread_client = connect_to_google_sheets()
        sheet = gspread_client.open(config.SHEET_NAME)
        worksheet = sheet.worksheet(AUTOMATOR_WORKSHEET_NAME)
        df = get_data_from_sheet(worksheet)
        driver = get_humanlike_driver()
        
        for i, (df_index, row) in enumerate(df.iterrows()):
            keyword = str(row.get('Keyword', '')).strip()
            target_url = str(row.get('Company1', '')).strip()
            original_row_index = row['original_index']
            logging.info(f"\n--- Processing keyword {i+1}/{len(df)}: '{keyword}' ---")
            
            if not keyword or not target_url:
                logging.warning(f"Skipping row {original_row_index} due to missing Keyword or Company1 URL.")
                continue
            
            driver.get(config.SEARCH_URL)
            time.sleep(random.uniform(DELAY_CONFIG["after_page_load"]["min"], DELAY_CONFIG["after_page_load"]["max"]))
            
            if not find_and_type_in_search_box(driver, keyword):
                continue
            
            time.sleep(random.uniform(DELAY_CONFIG["after_page_load"]["min"], DELAY_CONFIG["after_page_load"]["max"]))

            if random.random() < DETOUR_PROBABILITY:
                perform_random_detour(driver, target_url)

            final_rank, final_url = "Not Found", ""
            current_rank_offset = 0
            page_num = 1
            
            while page_num <= MAX_PAGES_TO_SCRAPE:
                logging.info(f"--- Scraping Page {page_num} for '{keyword}' (pausing to simulate reading) ---")
                time.sleep(random.uniform(DELAY_CONFIG["serp_read"]["min"], DELAY_CONFIG["serp_read"]["max"]))
                
                if driver.find_elements(By.CSS_SELECTOR, 'iframe[title="reCAPTCHA"]'):
                    if handle_captcha(driver, keyword):
                        continue
                    else:
                        break

                rank_on_page, url_on_page = find_rank_and_url(driver, target_url, current_rank_offset)
                if rank_on_page != "Not Found":
                    final_rank, final_url = rank_on_page, url_on_page
                    logging.info(f"Found at Rank {final_rank} on page {page_num}. URL: {final_url}")
                    break 
                
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, serp_selectors.NEXT_PAGE_BUTTON)
                    logging.info("Moving to next page...")
                    time.sleep(random.uniform(DELAY_CONFIG["before_next_page"]["min"], DELAY_CONFIG["before_next_page"]["max"]))
                    driver.execute_script("arguments[0].click();", next_button)
                    current_rank_offset += 10
                except NoSuchElementException:
                    logging.info("No 'Next' button found. Reached the end of results.")
                    break
                
                page_num += 1
            
            logging.info(f"Finished scraping for '{keyword}'. Final Rank: {final_rank}")
            worksheet.update_cell(original_row_index, 3, str(final_rank))
            worksheet.update_cell(original_row_index, 4, final_url)
            logging.info(f"Updated Sheet for row {original_row_index}.")
            
            logging.info("Taking a break before the next keyword...")
            time.sleep(random.uniform(DELAY_CONFIG["between_keywords"]["min"], DELAY_CONFIG["between_keywords"]["max"]))

    except Exception as e:
        error_traceback = traceback.format_exc()
        logging.critical(f"A critical, unhandled error occurred: {e}\n{error_traceback}")
        email_body = f"The Ranking Automator script has crashed due to an unhandled error.\n\nError:\n{e}\n\nTraceback:\n{error_traceback}"
        send_error_email("Ranking Automator Alert: SCRIPT CRASHED", email_body)
        
    finally:
        if driver:
            logging.info("Closing WebDriver.")
            driver.quit()
        logging.info("--- Ranking Automator Script Finished ---")