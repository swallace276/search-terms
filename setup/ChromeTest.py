from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set up the service
service = Service('/usr/local/bin/chromedriver')

# Initialize the driver
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.google.com/")
    print("WebDriver initialized successfully")
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'driver' in locals():
        time.sleep(2)
        driver.quit()
