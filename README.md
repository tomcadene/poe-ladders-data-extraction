# poe-ladders-data-extraction
A collection of scripts used to extract data from the Path of Exile ladders

I do recommend using different chrome profiles for each script if you are running several scripts at the same time

# Scripts

## find_account_characters
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

