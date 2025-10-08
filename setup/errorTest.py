from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.chrome import ChromeType
#from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Use specific ChromeDriver version
service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("WebDriver initialized successfully")
except Exception as e:
    print(f"An error occurred: {e}")