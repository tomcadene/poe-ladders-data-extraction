# poe-ladders-data-extraction
A collection of scripts used to extract data from the Path of Exile ladders

I do recommend using different chrome profiles for each script if you are running several scripts at the same time

# Scripts
+ `find_account_characters.py`
  + The script will navigate to the specified POE leaderbaord page, find, print and log an account characters. Every X seconds the script will reload the page and repeat the process.
+ `save_ladder_data.py`
  + The script will navigate to the specified POE leaderbaord page, find, print, log and save all the ladder characters in a json file. Every X seconds the script will reload the page and repeat the process.

## `find_account_characters.py`
The script will navigate to the specified POE leaderbaord page, find, print and log an account characters. Every X seconds the script will reload the page and repeat the process.

### Environment Variables
The script loads configurations from a `.env` file. Ensure this file is in the same directory as your script.

### Fetching and Parsing the Leaderboard
`fetch_leaderboard` Function: Navigates to the specified POE leaderboard page and waits until the leaderboard table is present using Selenium's `WebDriverWait`.

`parse_leaderboard` Function: 
+ Locates the leaderboard table and iterates through each row.
+ Extracts account details, checking if the account matches the specified `ACCOUNT`.
+ Handles both alive and dead characters by checking for the presence of the (Dead) span.
+ Collects relevant character information into a dictionary.

`log_characters` Function: Logs each found character's details both to the console and the log file.

### Main Loop
The script runs indefinitely, fetching and parsing the leaderboard every 60 seconds.  
Gracefully handles interruptions `(Ctrl+C)` and ensures the WebDriver closes properly upon exit.

### Running the Script
Ensure All Dependencies Are Installed  
`pip install selenium python-dotenv`

Verify Chromedriver and Chrome Executable Paths  
Ensure that the paths specified in your `.env` file (`CHROMEDRIVER_PATH` and `CHROME_EXECUTABLE_PATH`) are correct.  
Chromedriver Compatibility: The version of Chromedriver must match your installed Chrome browser version.

Execute the Script
`python find_account_characters.py`

## `save_ladder_data.py`
The script will navigate to the specified POE leaderbaord page, find, print, log and save all the ladder characters in a json file. Every X seconds the script will reload the page and repeat the process.

### Automated Ladder Scraping Every Minute
+ The script continuously accesses the specified POE ladder page, scraping the latest leaderboard data every 60 seconds. This ensures that you have up-to-date information without manual intervention.

### Comprehensive Data Extraction and Storage
+ It meticulously extracts relevant details for each character, including rank, account name, character name, class, level, experience, and death status. The extracted data is saved in neatly formatted JSON files within a dedicated `ladder_data` directory, each named with a precise timestamp for easy organization and retrieval.

### Robust Logging and Real-Time Feedback
+ The script provides extensive logging capabilities by recording all activities, successes, and errors in a `ladder_scraper.log` file. Additionally, it prints real-time status updates to the console, allowing you to monitor its operations and quickly identify any issues.

### Configurable via Environment Variables
+ Flexibility is achieved through the use of a `.env` file, where you can easily set and modify essential configurations such as the paths to `chromedriver`, Chrome profile, Chrome executable, and the POE ladder URL. This makes the script adaptable to different environments and setups without altering the core code.

### Headless Operation with Custom Chrome Configurations
+ Utilizing Selenium in headless mode, the script runs efficiently in the background without opening a visible browser window. It also leverages custom Chrome profiles and executable paths, ensuring that it operates seamlessly within your specified Chrome environment and maintains any necessary session data.
