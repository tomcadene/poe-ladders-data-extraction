import os
import time
import logging
from logging.handlers import RotatingFileHandler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
CHROME_PROFILE_PATH = os.getenv('CHROME_PROFILE_PATH')
CHROME_EXECUTABLE_PATH = os.getenv('CHROME_EXECUTABLE_PATH')
POE_LADDER_PAGE = os.getenv('POE_LADDER_PAGE')
ACCOUNT = os.getenv('ACCOUNT')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'poe_ladder_log.log') 

# Validate essential environment variables
required_vars = [
    'CHROMEDRIVER_PATH',
    'CHROME_PROFILE_PATH',
    'CHROME_EXECUTABLE_PATH',
    'POE_LADDER_PAGE',
    'ACCOUNT'
]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Set up logging with RotatingFileHandler
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a rotating file handler
handler = RotatingFileHandler(
    LOG_FILE_PATH,
    maxBytes=5*1024*1024,  # 5 MB per log file
    backupCount=5,         # Keep up to 5 backup log files
    encoding='utf-8'
)

# Define log message format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add handler to the logger
logger.addHandler(handler)

def setup_driver():
    print("[INFO] Setting up Chrome options...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")  # Specify custom profile
    chrome_options.binary_location = CHROME_EXECUTABLE_PATH  # Specify custom Chrome executable

    # Optional: Add other options for better stability
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    print("[INFO] Initializing WebDriver with Service object...")
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )
    print("[INFO] WebDriver initialized successfully.")
    return driver

def fetch_leaderboard(driver):
    try:
        print(f"[INFO] Navigating to {POE_LADDER_PAGE}...")
        driver.get(POE_LADDER_PAGE)
        print("[INFO] Page loaded successfully.")
        # Wait until the leaderboard table is present
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.league-ladder__entries"))
        )
        print("[INFO] Leaderboard table is present.")
    except Exception as e:
        print(f"[ERROR] Failed to load the page or locate the leaderboard table: {e}")
        logger.error(f"Failed to load the page or locate the leaderboard table: {e}")

def parse_leaderboard(driver):
    characters = []
    try:
        print("[INFO] Locating the leaderboard table...")
        table = driver.find_element(By.CSS_SELECTOR, "table.league-ladder__entries")
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        print(f"[INFO] Found {len(rows)} rows in the leaderboard.")

        for index, row in enumerate(rows, start=1):
            try:
                # Extract all <td> elements in the row
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) < 6:
                    print(f"[WARNING] Row {index} does not have enough columns.")
                    continue

                # Extract account name
                account_td = tds[1]
                account_link = account_td.find_element(By.TAG_NAME, "a")
                account_name = account_link.text.strip()
                print(f"[DEBUG] Row {index}: Account Name - {account_name}")

                if account_name.lower() == ACCOUNT.lower():
                    print(f"[INFO] Match found for account: {ACCOUNT} in row {index}")
                    
                    # Extract other details
                    rank = tds[0].text.strip()
                    
                    # Extract character name and check if dead
                    character_td = tds[2]
                    try:
                        dead_span = character_td.find_element(By.CSS_SELECTOR, "span.league-ladder__entry-state")
                        is_dead = "Dead" in dead_span.text
                        # Remove the (Dead) text from character name
                        character_name = character_td.text.replace(dead_span.text, '').strip('" ').strip()
                    except NoSuchElementException:
                        character_name = character_td.text.strip('" ').strip()
                        is_dead = False

                    char_class = tds[3].text.strip()
                    level = tds[4].text.strip()
                    experience = tds[5].text.strip()

                    character_info = {
                        "Rank": rank,
                        "Account": account_name,
                        "Character": character_name,
                        "Class": char_class,
                        "Level": level,
                        "Experience": experience,
                        "Dead": is_dead
                    }

                    characters.append(character_info)
                    print(f"[INFO] Character found: {character_info}")

            except IndexError:
                print(f"[WARNING] Row {index} does not have enough columns.")
            except Exception as e:
                print(f"[ERROR] Error parsing row {index}: {e}")
                logger.error(f"Error parsing row {index}: {e}")

    except NoSuchElementException:
        print("[ERROR] Leaderboard table not found on the page.")
        logger.error("Leaderboard table not found on the page.")
    except Exception as e:
        print(f"[ERROR] An error occurred while parsing the leaderboard: {e}")
        logger.error(f"An error occurred while parsing the leaderboard: {e}")

    return characters

def log_characters(characters):
    if not characters:
        print("[INFO] No characters found for the specified account.")
        logger.info("No characters found for the specified account.")
        return

    for char in characters:
        log_message = (
            f"Rank: {char['Rank']}, "
            f"Account: {char['Account']}, "
            f"Character: {char['Character']}, "
            f"Class: {char['Class']}, "
            f"Level: {char['Level']}, "
            f"Experience: {char['Experience']}, "
            f"Dead: {char['Dead']}"
        )
        print(f"[LOG] {log_message}")
        logger.info(log_message)

def main():
    print("[INFO] Starting the POE Ladder Tracker script.")
    driver = setup_driver()

    try:
        while True:
            print("[INFO] Fetching the leaderboard...")
            fetch_leaderboard(driver)
            print("[INFO] Parsing the leaderboard for account:", ACCOUNT)
            characters = parse_leaderboard(driver)
            log_characters(characters)
            print("[INFO] Sleeping for 60 seconds before the next check.")
            time.sleep(60)  # Wait for 1 minute before reloading
    except KeyboardInterrupt:
        print("\n[INFO] Script interrupted by user. Exiting...")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        print("[INFO] Closing the WebDriver.")
        driver.quit()
        print("[INFO] Script terminated.")

if __name__ == "__main__":
    main()
