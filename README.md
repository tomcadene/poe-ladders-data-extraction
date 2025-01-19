# poe-ladders-data-extraction
A collection of scripts used to extract data from the Path of Exile ladders

I do recommend using different chrome profiles for each script if you are running several scripts at the same time

# Scripts
* 🕵 `find_account_characters.py`
  * The script will navigate to the specified POE leaderbaord page, find, print and log an account characters. Every X seconds the script will reload the page and repeat the process.
* 💾 `save_ladder_data.py`
  * The script will navigate to the specified POE leaderbaord page, find, print, log and save all the ladder characters in a json file. Every X seconds the script will reload the page and repeat the process.
* `save_new_characters.py`
  * The script will navigate to the specified POE leaderbaord page, find, print, log and save all the characters and new characters in a json file. Every X seconds the script will reload the page and repeat the process.

## `find_account_characters.py`
The script will navigate to the specified POE leaderbaord page, find, print and log an account characters. Every X seconds the script will reload the page and repeat the process.

### Environment Setup
+ Loads and validates necessary environment variables from a .env file.

### Logging Mechanism
+ Utilizes rotating file handlers to manage log files efficiently.

### WebDriver Configuration
+ Sets up a headless Chrome WebDriver with custom profiles and options.

### Leaderboard Scraping
+ Navigates and extracts specific account character details from the POE leaderboard.

### Continuous Monitoring
+ Runs in a loop, fetching and logging leaderboard data every 60 seconds.

## `save_ladder_data.py`
The script will navigate to the specified POE leaderbaord page, find, print, log and save all the ladder characters in a json file. Every X seconds the script will reload the page and repeat the process.

### Environment Management
+ Loads and validates required environment variables from a .env file.

### Logging Setup
+ Configures logging to file with timestamped entries for monitoring activities.

### WebDriver Configuration
+ Initializes a headless Chrome WebDriver with custom profiles and executable paths.

### Data Scraping
+ Extracts character details from the Path of Exile leaderboard page using Selenium.

### JSON Data Storage
+ Saves scraped data into timestamped JSON files within a designated directory.

## `save_new_characters.py`
The script will navigate to the specified POE leaderbaord page, find, print, log and save all the characters and new characters in a json file. Every X seconds the script will reload the page and repeat the process.

### Environment Configuration
+ Loads settings from a .env file using the dotenv library

### Automated Browser Control
+ Uses Selenium WebDriver to navigate and interact with the leaderboard page.

### Periodic Monitoring
+ Refreshes and checks the leaderboard every 60 seconds for updates.

### New Character Detection
+ Identifies and records new characters, saving their data in organized directories.

### Comprehensive Logging
+ Logs activities and errors to both a file and the console for easy tracking.
