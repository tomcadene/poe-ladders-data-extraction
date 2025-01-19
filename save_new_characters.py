import os
import json
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
CHROME_PROFILE_PATH = os.getenv('CHROME_PROFILE_PATH')
CHROME_EXECUTABLE_PATH = os.getenv('CHROME_EXECUTABLE_PATH')
POE_LADDER_PAGE = os.getenv('POE_LADDER_PAGE')
ACCOUNT = os.getenv('ACCOUNT')

# Constants
CHECK_INTERVAL = 60  # in seconds
CHARACTERS_FILE = 'characters.json'
NEW_CHARACTERS_DIR = 'new_characters'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("poe_ladder_monitor.log"),
        logging.StreamHandler()
    ]
)

def setup_driver(headless=True):
    """Setup Selenium WebDriver with custom paths and headless mode."""
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    chrome_options.binary_location = CHROME_EXECUTABLE_PATH
    
    if headless:
        chrome_options.add_argument("--headless")  # Enable headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional but recommended)
        chrome_options.add_argument("--window-size=1920,1080")  # Set window size to ensure all elements are loaded properly
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, required for some environments
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    # Optional: Disable logging (suppressing unnecessary logs)
    chrome_options.add_argument("--log-level=3")  # Suppress logs except for errors

    # Create a Service object
    service = Service(CHROMEDRIVER_PATH)

    # Initialize the WebDriver with the Service object
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def load_existing_characters():
    """Load existing characters from characters.json."""
    if not os.path.exists(CHARACTERS_FILE):
        logging.info(f"{CHARACTERS_FILE} not found. Creating a new one.")
        with open(CHARACTERS_FILE, 'w') as f:
            json.dump([], f)
        return []
    with open(CHARACTERS_FILE, 'r') as f:
        try:
            data = json.load(f)
            logging.info(f"Loaded {len(data)} existing characters.")
            return data
        except json.JSONDecodeError:
            logging.error(f"Error decoding {CHARACTERS_FILE}. Starting with an empty list.")
            return []

def save_characters(characters):
    """Save characters to characters.json."""
    with open(CHARACTERS_FILE, 'w') as f:
        json.dump(characters, f, indent=4)
    logging.info(f"Saved {len(characters)} characters to {CHARACTERS_FILE}.")

def save_new_character(character_data):
    """Save new character data in a structured folder."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    # Sanitize folder name components to avoid filesystem issues
    account_name_safe = character_data['account_name'].replace("#", "_")
    character_name_safe = "".join([c if c.isalnum() or c in (" ", "_") else "_" for c in character_data['character_name']])
    folder_name = f"new_character_{character_data['rank']}_{account_name_safe}_{character_name_safe}_{character_data['class']}_{character_data['level']}_{character_data['status']}_{timestamp}"
    folder_path = os.path.join(NEW_CHARACTERS_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, 'character.json')
    with open(file_path, 'w') as f:
        json.dump(character_data, f, indent=4)
    logging.info(f"New character saved: {folder_name}")

def parse_character_row(row):
    """Parse a table row and extract character data."""
    try:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if len(cells) < 6:
            logging.warning("Unexpected number of cells in row. Skipping.")
            return None

        rank = cells[0].text.strip()
        account_element = cells[1].find_element(By.TAG_NAME, 'a')
        account_name = account_element.text.strip()

        character_cell = cells[2]
        # Extract character name and status
        character_name = character_cell.text.strip()
        status = 'alive'
        if '(Dead)' in character_name:
            status = 'dead'
            character_name = character_name.replace('(Dead)', '').strip('" ').strip()
        else:
            character_name = character_name.strip('" ').strip()

        char_class = cells[3].text.strip()
        level = cells[4].text.strip()
        experience = cells[5].text.strip()

        character_data = {
            'rank': rank,
            'account_name': account_name,
            'character_name': character_name,
            'class': char_class,
            'level': level,
            'experience': experience,
            'status': status
        }
        return character_data
    except Exception as e:
        logging.error(f"Error parsing row: {e}")
        return None

def main():
    # Ensure new_characters directory exists
    os.makedirs(NEW_CHARACTERS_DIR, exist_ok=True)

    # Load existing characters
    existing_characters = load_existing_characters()

    # Initialize WebDriver in headless mode
    driver = setup_driver(headless=True)  # Set to False if you want to see the browser

    driver.get(POE_LADDER_PAGE)
    logging.info(f"Navigated to {POE_LADDER_PAGE}")

    try:
        while True:
            logging.info("Refreshing the ladder page...")
            driver.refresh()
            time.sleep(5)  # Wait for the page to load

            # Locate the leaderboard table
            try:
                table = driver.find_element(By.CSS_SELECTOR, 'table.league-ladder__entries')
                tbody = table.find_element(By.TAG_NAME, 'tbody')
                rows = tbody.find_elements(By.CSS_SELECTOR, 'tr.league-ladder__entry')
                logging.info(f"Found {len(rows)} rows in the leaderboard.")
            except Exception as e:
                logging.error(f"Error locating leaderboard table: {e}")
                time.sleep(CHECK_INTERVAL)
                continue

            for row in rows:
                character = parse_character_row(row)
                if character is None:
                    continue

                # Check if the account matches
                if character['account_name'] != ACCOUNT:
                    continue

                # Check if character is already recorded
                is_existing = any(
                    c['account_name'] == character['account_name'] and
                    c['character_name'] == character['character_name']
                    for c in existing_characters
                )

                if not is_existing:
                    # New character found
                    logging.info(f"New character found: {character['character_name']}")
                    save_new_character(character)
                    existing_characters.append(character)
                else:
                    logging.debug(f"Character already exists: {character['character_name']}")

            # Save updated characters list
            save_characters(existing_characters)

            logging.info(f"Waiting for {CHECK_INTERVAL} seconds before next check.")
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        driver.quit()
        logging.info("WebDriver closed.")

if __name__ == "__main__":
    main()
