Ranking Automation Tool
![alt text](https://img.shields.io/badge/Python-3.8+-blue.svg)

![alt text](https://img.shields.io/badge/License-MIT-yellow.svg)
<!-- Assuming a standard license, can be changed -->
Welcome to the Ranking Automation Tool! This powerful Python script automates the process of checking Google search rankings for your website, saving you hours of manual work and providing accurate, up-to-date data directly in a Google Sheet.
🚀 Key Features
Fully Automated Ranking Checks: Just add your keywords and target URL to a Google Sheet, and the tool does the rest.
Google Sheets Integration: Manages all input and output in one convenient, cloud-based Google Sheet.
Human-Like Browsing: Uses a real Chrome browser profile, random delays, and rotating user agents to appear like a real user, reducing the chance of being blocked.
CAPTCHA Handling: If a CAPTCHA is detected, the script pauses, sends you an email alert, and waits for you to solve it manually before continuing.
Detailed Logging: Every action—each search, page scraped, and result found—is recorded in a local log file so you always know what's happening.
Email Error Alerts: If the script crashes or requires your attention (like for a CAPTCHA), it automatically sends an email to you.
##📋 Prerequisites
Before you begin, ensure you have the following installed and set up:
Python: Version 3.8 or newer is recommended.
Google Chrome: The automation uses Chrome, so you must have it installed.
A Code Editor: A program like VS Code is highly recommended for editing configuration files.
A Dedicated Google Account: A separate Gmail account (e.g., yourcompany.automation@gmail.com) is recommended for this process to avoid conflicts with your personal account.
🔧 Installation & Setup
This is a one-time setup process. Follow these steps carefully.
Step 1: Set Up Google Cloud Platform (GCP) API
This allows the script to securely access your Google Sheet.
Go to the Google Cloud Console.
Create a new project (e.g., "Ranking Automation Project").
Enable the Google Drive API and Google Sheets API for your project.
Navigate to Credentials > + CREATE CREDENTIALS > Service account.
Give the service account a name (e.g., "sheets-automator") and click CREATE AND CONTINUE.
Assign the Project > Editor role. Click CONTINUE, then DONE.
Click on the email address of the newly created service account.
Go to the KEYS tab, click ADD KEY > Create new key.
Choose JSON as the key type and click CREATE.
A .json file will be downloaded. This file is your password! Keep it safe.
Rename this file to gcp_credentials.json.
Step 2: Set Up Your Google Sheet
Make a Copy: Open the Ranking Automation Sheet Template and make a copy (File > Make a copy) in your own Google Drive.
Share the Sheet:
Open the gcp_credentials.json file you downloaded. Find the value for "client_email". It will look like something@...gserviceaccount.com.
In your new Google Sheet, click the Share button.
Paste the client_email address, give it Editor permissions, and click Send.
Step 3: Set Up Your Local Project
Create Project Folder: Create a new folder on your computer named Ranking_Automation.
Move Files: Place all the project files (.py files, requirements.txt, etc.) and your gcp_credentials.json file into this folder.
Set Up Virtual Environment: Open a terminal or command prompt, navigate to your project folder, and run the following commands:

# Navigate to your project folder
cd path/to/Ranking_Automation

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
Step 4: Configure the Automation
Open the config.py file in your code editor and update the following settings:
PROJECT_ROOT: Set this to the absolute path of your Ranking_Automation folder (e.g., r"C:\Users\YourName\Documents\Ranking_Automation").
SHEET_NAME: Enter the exact name of your Google Sheet copy (e.g., "Copy of Ranking Automation").
WORKSHEET_NAME: Enter the name of the tab within your sheet (default is "Ranking Automator").
Email Notification Settings:
ENABLE_EMAIL_NOTIFICATIONS: Set to True to receive alerts.
SENDER_EMAIL: The Gmail address you want to send alerts from.
SENDER_PASSWORD: This is NOT your regular Gmail password. You must generate a 16-digit App Password.
Go to your Google Account settings > Security.
Turn on 2-Step Verification.
Go to "App passwords", create a new one for "Mail" on "Windows Computer", and copy the password.
RECIPIENT_EMAIL: The email address where you want to receive alerts.
Step 5: Create Your Master Chrome Profile
This creates a dedicated, logged-in Chrome profile to help avoid CAPTCHAs.
Make sure your virtual environment is still active in your terminal.
Run the profile creation script:

python create_master_profile.py
A new Chrome window will open. You have 90 seconds to:
Go to google.com.
Sign in to your dedicated Google Account.
Accept any cookie pop-ups.
IMPORTANT: If Google asks to "Turn on sync?", click "No thanks".
Once signed in, you can manually close the browser. The script will finish, and your profile is ready.
▶️ How to Use
Daily Workflow
Add Keywords: Open your Google Sheet and add new keywords and their corresponding target URLs to the bottom of the list.
Leave Ranking Columns Blank: The script identifies which keywords to process by looking for empty cells in the Rankings column.
Run the Automation: Follow the steps below.
Running the Script
To start the tool at any time, open your terminal and run these three commands:

# 1. Go to your project folder
cd path/to/Ranking_Automation

# 2. Activate the Python environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 3. Run the main script
python ranking_automator.py
The script will begin its work. You can watch its progress in the terminal and see the results appear in your Google Sheet in real-time.
Stopping the Script
To stop the script while it's running, simply press Ctrl + C in the terminal window.
💡 Advanced Strategies
Checking Rankings for Different Locations
Use a VPN or location-spoofer browser extension.
Install Extension: Install a location-changing extension in your regular Chrome browser.
Enable in Master Profile: When you run create_master_profile.py, install and configure the extension in the special Chrome window that opens. Set it to your first desired location (e.g., Mumbai).
Structure Your Keyword List: Group all keywords for one location together in the Google Sheet.
Use the "Buffer" Technique:
After a block of location-specific keywords (e.g., 100 Mumbai keywords), add 5-10 "dummy" keywords.
Run the script.
When it starts processing the dummy keywords, stop the script (Ctrl + C).
Manually open Chrome, switch the extension to the next location (e.g., Bangalore).
Relaunch the script. It will pick up where it left off, now searching from the new location.
Handling CAPTCHAs
Script Pauses: The tool detects the CAPTCHA and pauses.
You Get an Alert: You will receive an email (if configured) and see a message in the terminal.
Solve it Manually: The Chrome browser window will remain open. Go to that window and solve the CAPTCHA.
Script Resumes: Once solved, the script automatically detects it and continues its work.
❓ Troubleshooting (FAQ)
Q: I get a FileNotFoundError when I run the script.
A: This is usually an incorrect path in config.py.
Check that PROJECT_ROOT is the full, correct absolute path to your project folder.
Ensure the gcp_credentials.json file is in the project folder and spelled correctly.
Q: I get a gspread.exceptions.SpreadsheetNotFound error.
A: The script can't find your Google Sheet.
Check that SHEET_NAME in config.py exactly matches your Google Sheet's name (it's case-sensitive).
Make sure you have shared the sheet with the client_email from your .json file and given it "Editor" permissions.
Q: All my rankings are "Not Found", but I know my site ranks!
A: This could be a few things:
URL Mismatch: The URL in your sheet (e.g., mywebsite.com) must be a part of the URL that appears in Google's search results (e.g., https://www.mywebsite.com/blog/article). Using the base domain is usually safest.
Location Mismatch: The script searches from your computer's location. If you're tracking ranks for a different country, the results will differ. See the "Advanced Strategies" section.
Google HTML Changes: Google occasionally updates its page layout, which can break the script. This may require a developer to update the selectors in the code.
