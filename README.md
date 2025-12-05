# Testing TFDD Events Search Protocols

## Abstract
The International Freshwater Events Dataset uses a collection of news articles to summarize conflict and cooperation events in transboundary freshwater basins. This report summarizes the novel methods utilized in the 2025 update to the Events Dataset, including the use of two LLMs to complete discrete natural language processing (NLP) tasks, and a geospatial model to collect crowdsourced names data using OpenStreetMap (OSM). In a comparison of the original search protocol, the published data from the 2008 Events Dataset, and the new protocol, we found individual cases wherein OSM data inclusion and LLM transliteration have the potential to improve discovery of new events. This study also found that the untrained LLM filtered out key relevant articles from the resulting dataset. Further research, model training, and model validation are necessary to improve this method's ability to capture a more representative sample of conflict and cooperation events in transboundary basins.

## Repository contents
- Code
- * Classes - the main script will use the Python classes in this folder for different behavior, including logging in to Nexis Uni (LoginClass.py), the search process (SearchClass.py), downloading (DownloadClass.py), as well as file format conversions needed in the process
- * For_figs - contains py sripts to create figures from EDA in Figs folder
- * Notebooks - notebooks for exploratory data analysis and for creating dataframes for input to script
- * app.py this is the main file that will be run in terminal
- * utils.py - the full process lives here
- Data
- * Downloads folder - contains downloaded results for each basin code and search protocol
- * Excel, csv, and txt files for input to streamlit app and/or 
- Figs - destination path for figures
- Setup
- * downloads or updates driver as needed for functioning selenium script
- * mac_setup.sh - run to set up for Mac
- * win_setup.bat - run to set up for Windows
- * requirements.txt - contains the packages and libraries needed to run the script

## Setup instructions
Note: you only have to do this once on your machine
- Ensure you have Chrome browser and that it has been opened recently
- In your Terminal enter

```
git clone https://github.com/swallace276/search-terms.git # can skip if already cloned
cd search-terms/Setup 
```

- According to your operating system, enter one of these lines in your Terminal
```
.\win_setup.bat #if you have a Windows
./mac_setup.sh #if you have a Mac
``` 
- * This step *should* run download_driver.py, but sometimes it fails. If it tells you "ChromeDriver not found", just open a Chrome browser window and then go back to your Terminal and run 
```
download_driver.py
```
- Now you're all set up! go back to your search-terms base directory
```
cd ..
```

## How to run
- Navigate to the search-terms folder if not there already.
- Activate the virtual environment for your OS:
```
venv\Scripts\activate # if Windows
source venv/bin/activate # if Mac
```
- Then enter
```
streamlit run Code/app.py
```
- * A new window or tab will open in your Chrome browser. The first time you run this it may take a minute. When the window loads, 
- Enter your UA username in the field 'username'
- Select the search protocol you want to test.
- In the field "Select basin code(s)" start typing the name of the basin(s) you want to test and click on the correct BCODE. You can choose multiple by repeating the selection. If you want to run a search on all single event basins, click the checkbox and all basins in this list will auto-populate.
- When ready to download, click "Start Download"
- Go back to your terminal and type your UA password. The characters will not appear as you type them, so take your time.
- Watch it run!

## Troubleshooting
For help troubleshooting errors in the script, [this doc](https://oregonstate.box.com/s/ggbgtrhw9fdijxzob8n4p8kcfwvg0pu9) has a list of common issues and their solutions. For other questions please reach out to [Selena Wallace](wallasel@oregonstate.edu). 

## Acknowledgments
This project is an adapted and automated version of a data collection process developed by the Shared Waters Lab partnership between Oregon State University, Tufts University, and IHE Delft.