import os
import time
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
CHROME_PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH")
CHROME_EXECUTABLE_PATH = os.getenv("CHROME_EXECUTABLE_PATH")
POE_LADDER_PAGE = os.getenv("POE_LADDER_PAGE")

# Validate environment variables
if not all([CHROMEDRIVER_PATH, CHROME_PROFILE_PATH, CHROME_EXECUTABLE_PATH, POE_LADDER_PAGE]):
    raise ValueError("One or more environment variables are missing. Please check your .env file.")

# Setup logging
logging.basicConfig(
    filename='ladder_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create ladder_data directory if it doesn't exist
DATA_DIR = "ladder_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"Created directory: {DATA_DIR}")
    logging.info(f"Created directory: {DATA_DIR}")

# Configure Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")  # Custom Chrome profile
chrome_options.binary_location = CHROME_EXECUTABLE_PATH  # Custom Chrome executable

# Initialize Selenium WebDriver
try:
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("Initialized Chrome WebDriver successfully.")
    logging.info("Initialized Chrome WebDriver successfully.")
except WebDriverException as e:
    print(f"Error initializing Chrome WebDriver: {e}")
    logging.error(f"Error initializing Chrome WebDriver: {e}")
    raise e

def scrape_ladder():
    """
    Scrapes the ladder data from the POE ladder page.
    Returns a list of character dictionaries.
    """
    characters = []
    try:
        driver.get(POE_LADDER_PAGE)
        print(f"Accessed POE ladder page: {POE_LADDER_PAGE}")
        logging.info(f"Accessed POE ladder page: {POE_LADDER_PAGE}")
        
        # Wait for the table to load
        time.sleep(5)  # Adjust as necessary for page load time

        # Locate the table body
        tbody = driver.find_element(By.CSS_SELECTOR, "table.league-ladder__entries tbody")
        rows = tbody.find_elements(By.CSS_SELECTOR, "tr.league-ladder__entry")
        print(f"Found {len(rows)} rows in the ladder.")
        logging.info(f"Found {len(rows)} rows in the ladder.")

        for row in rows:
            try:
                # Extract cells
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 6:
                    print("Row does not have enough cells. Skipping.")
                    logging.warning("Row does not have enough cells. Skipping.")
                    continue

                rank = cells[0].text.strip()
                account_element = cells[1].find_element(By.TAG_NAME, "a")
                account_name = account_element.text.strip()
                character_name = cells[2].text.strip().strip('"').strip()
                character_class = cells[3].text.strip()
                level = cells[4].text.strip()
                experience = cells[5].text.strip()

                # Check if character is dead
                try:
                    dead_element = cells[2].find_element(By.CLASS_NAME, "league-ladder__entry-state")
                    status = dead_element.text.strip().strip("()")
                    is_dead = True if "Dead" in status else False
                except NoSuchElementException:
                    is_dead = False

                character = {
                    "rank": rank,
                    "account_name": account_name,
                    "character_name": character_name,
                    "class": character_class,
                    "level": level,
                    "experience": experience,
                    "is_dead": is_dead
                }

                characters.append(character)
                print(f"Scraped character: {character}")
                logging.info(f"Scraped character: {character}")

            except Exception as e:
                print(f"Error parsing row: {e}")
                logging.error(f"Error parsing row: {e}")
                continue

    except TimeoutException as e:
        print(f"Timeout while loading the page: {e}")
        logging.error(f"Timeout while loading the page: {e}")
    except NoSuchElementException as e:
        print(f"Error finding elements on the page: {e}")
        logging.error(f"Error finding elements on the page: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logging.error(f"An unexpected error occurred: {e}")

    return characters

def save_to_json(data):
    """
    Saves the scraped data to a JSON file with a timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ladder_data_{timestamp}.json"
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Saved data to {filepath}")
        logging.info(f"Saved data to {filepath}")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")
        logging.error(f"Error saving data to JSON: {e}")

def main():
    print("Starting ladder scraper. Press Ctrl+C to stop.")
    logging.info("Ladder scraper started.")
    try:
        while True:
            print(f"\nScraping ladder data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logging.info("Starting new scrape cycle.")

            characters = scrape_ladder()
            if characters:
                save_to_json(characters)
                print(f"Total characters scraped: {len(characters)}")
                logging.info(f"Total characters scraped: {len(characters)}")
            else:
                print("No characters found during this scrape.")
                logging.warning("No characters found during this scrape.")

            print("Waiting for 60 seconds before the next scrape.")
            logging.info("Waiting for 60 seconds before the next scrape.")
            time.sleep(60)  # Fixed 60 seconds wait after saving data

    except KeyboardInterrupt:
        print("\nScript terminated by user.")
        logging.info("Ladder scraper terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred in the main loop: {e}")
        logging.error(f"An unexpected error occurred in the main loop: {e}")
    finally:
        driver.quit()
        print("Closed Chrome WebDriver.")
        logging.info("Closed Chrome WebDriver.")

if __name__ == "__main__":
    main()
