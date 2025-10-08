import platform
import sys
import subprocess
import re
import requests
import os
import shutil
import json
from zipfile import ZipFile
from io import BytesIO
from tqdm import tqdm

def get_operating_system():
    system = platform.system().lower()
    if system == "darwin":
        return "mac"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        print(f"Unsupported operating system: {system}")
        sys.exit(1)

def get_chrome_version():
    os = get_operating_system()
    try:
        if os == "mac":
            process = subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], stdout=subprocess.PIPE)
        elif os == "windows":
            process = subprocess.Popen(['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif os == "linux":
            process = subprocess.Popen(['google-chrome', '--version'], stdout=subprocess.PIPE)
        
        output, _ = process.communicate()
        version = re.search(r'\d+\.\d+\.\d+\.\d+', output.decode('utf-8')).group(0)
        return version
    except Exception as e:
        print(f"Error detecting Chrome version: {e}")
        return None

def get_matching_chromedriver_version(chrome_version):
    base_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    
    response = requests.get(base_url)
    if response.status_code == 200:
        versions_data = json.loads(response.text)
        for version_entry in versions_data['versions']:
            if version_entry['version'] == chrome_version:
                return version_entry['version']
        print(f"Exact match not found. Searching for closest version...")
        # If exact match not found, find the closest lower version
        chrome_version_parts = list(map(int, chrome_version.split('.')))
        closest_version = None
        for version_entry in versions_data['versions']:
            entry_version_parts = list(map(int, version_entry['version'].split('.')))
            if entry_version_parts <= chrome_version_parts and (closest_version is None or entry_version_parts > list(map(int, closest_version.split('.')))):
                closest_version = version_entry['version']
        if closest_version:
            print(f"Found closest version: {closest_version}")
            return closest_version
    else:
        print(f"Failed to fetch ChromeDriver versions. Status code: {response.status_code}")
    return None

def download_chromedriver(version, os_type):
    if not version:
        print("No matching ChromeDriver version found.")
        return False
    
    base_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing"
    if os_type == "mac":
        file_name = f"chromedriver-mac-x64.zip"
    elif os_type == "windows":
        file_name = f"chromedriver-win32.zip"
    elif os_type == "linux":
        file_name = f"chromedriver-linux64.zip"
    
    download_url = f"{base_url}/{version}/{os_type}/{file_name}"
    
    print(f"Downloading ChromeDriver from: {download_url}")
    try:
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad requests (4xx or 5xx)
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB

        with tqdm(total=total_size, unit='iB', unit_scale=True) as progress_bar:
            with open(f"./chromedriver_temp_{file_name}", 'wb') as file:
                for data in response.iter_content(block_size):
                    size = file.write(data)
                    progress_bar.update(size)
        
        print("ChromeDriver downloaded successfully.")
        
        with ZipFile(f"./chromedriver_temp_{file_name}", 'r') as zip_ref:
            zip_ref.extractall("./chromedriver_temp")
        
        os.remove(f"./chromedriver_temp_{file_name}")
        print("ChromeDriver extracted successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading ChromeDriver: {e}")
        return False

def move_chromedriver(os_type):
    source_path = "./chromedriver_temp/chromedriver-mac-x64/chromedriver" if os_type == "mac" else "./chromedriver_temp/chromedriver-win32/chromedriver.exe" if os_type == "windows" else "./chromedriver_temp/chromedriver-linux64/chromedriver"
    
    if os_type == "mac" or os_type == "linux":
        dest_path = "/usr/local/bin/chromedriver"
    elif os_type == "windows":
        dest_path = "C:\\Windows\\chromedriver.exe"
    
    try:
        shutil.move(source_path, dest_path)
        print(f"ChromeDriver moved to: {dest_path}")
        os.chmod(dest_path, 0o755)  # Make executable
        print("ChromeDriver permissions updated.")
    except Exception as e:
        print(f"Error moving ChromeDriver: {e}")
        print("You may need to run this script with administrator/root privileges.")
    
    # Clean up temporary directory
    shutil.rmtree("./chromedriver_temp")

# Main execution
os_type = get_operating_system()
print(f"Detected operating system: {os_type}")

chrome_version = get_chrome_version()
if chrome_version:
    print(f"Detected Chrome version: {chrome_version}")
    chromedriver_version = get_matching_chromedriver_version(chrome_version)
    if chromedriver_version:
        print(f"Matching ChromeDriver version: {chromedriver_version}")
        if download_chromedriver(chromedriver_version, os_type):
            move_chromedriver(os_type)
    else:
        print("Failed to find a matching ChromeDriver version. Please ensure you have the latest version of Chrome installed.")
else:
    print("Could not detect Chrome version. Please ensure Chrome is installed and you have the latest version.")