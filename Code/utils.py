from selenium.common.exceptions import SessionNotCreatedException, TimeoutException, NoSuchElementException

import os
import sys
import shutil
import time
import re
from tqdm import tqdm
import datetime
from pathlib import Path

# Add Code directory to path so we can import Classes
code_dir = os.path.dirname(os.path.abspath(__file__))
if code_dir not in sys.path:
    sys.path.insert(0, code_dir)

# Add repo root to path so we can import Setup
repo_root = os.path.abspath(os.path.join(code_dir, ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from Classes.LoginClass import PasswordManager, WebDriverManager, Login
from Classes.DownloadClass import Download, DownloadFailedException
from Classes.SearchClass import Search
from Setup import download_driver

_password_cache = None

def get_user(basin_code, uname, use_new_search=True):
    # Use standard paths that work for any user
    base_path = os.path.expanduser("~")
    # Get repo root (one level up from Code/)
    nexis_scraper_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    download_folder_temp = os.path.join(base_path, "Downloads")
    protocol_folder = "new_search" if use_new_search else "old_search"
    download_folder = os.path.join(nexis_scraper_folder, "Data", "Downloads", basin_code, protocol_folder)
    #download_folder = os.path.join(base_path, "Box", basin_code) # testing if we can download to Box drive from base path directly

    paths = {
        "base_path": base_path,
        "user_name": uname,
        "nexis_scraper_folder": nexis_scraper_folder,
        "download_folder_temp": download_folder_temp,
        "download_folder": download_folder, 
        "protocol": protocol_folder,  # Optional: useful for logging
    }
    
    return paths, uname

def logout_clearcookies(download):
    sign_in_button = "//button[@id='NexisUniMipNewSignIn']"
    try:
        download._click_from_xpath(sign_in_button)
        print("logging out")
    except Exception as e:
        #download.handle_popups() # maybe try this, sometimes the problem is the download dialog
        find_sign_in = download.driver.find_element_by_xpath(sign_in_button)
        download.driver.execute_script("return arguments[0].scrollIntoView(true);", find_sign_in)        
    download.driver.delete_all_cookies()
    print("deleting cookies")

def reset(download, login, search):
    logout_clearcookies(download)
    time.sleep(3)
    login._init_login()
    search.search_process()
    time.sleep(5)
    download.DownloadSetup()

def full_process(basin_code, username, paths, use_new_search=True):
    """
    Main download process function.
    
    Args:
        basin_code (str): The basin code for the geographic area
        username (str): Username from streamlit input
        paths (dict): Dictionary containing file paths
        use_new_search (bool): Whether to use new or old search protocol
        
    Returns:
        bool: True if download completed successfully, False otherwise
    """
    print("~" * 27)
    print(f"Starting download for {basin_code}!")
    print("~" * 27)

    download_folder = paths["download_folder"]
    download_folder_temp = paths["download_folder_temp"]
    
    # Create download folder if it doesn't exist
    if os.path.exists(download_folder):
        print(f"{basin_code} folder already exists")
    else:
        os.makedirs(download_folder, exist_ok=True) 
        print(f"created folder {basin_code}")
    
    # Password management
    global _password_cache
    if _password_cache is None:
        pm = PasswordManager()
        if not pm.password:
            print("No password found, please enter your password")
            password = pm.get_password()
            print("Password saved successfully")
        else:
            password = pm.password
        _password_cache = password
    else:
        password = _password_cache
        print("Using cached password")
    
    # WebDriver setup
    manager = WebDriverManager()

    try:
        driver = manager.start_driver()
    except SessionNotCreatedException:
        print("Session not created, updating driver...")
        download_driver.main()
        time.sleep(2)
        driver = manager.start_driver()

    # Login - using consistent username variable
    login = Login(user_name=username, password=password, driver_manager=manager, url=None)
    login._init_login()

    # Search process
    search = Search(driver, basin_code, username, paths["nexis_scraper_folder"], use_new_search=use_new_search)
    search.search_process()  


    # Download setup - streamlined parameters
    download = Download(
        driver=driver,
        basin_code=basin_code,
        username=username,
        login=login,
        search=search,
        download_folder=download_folder,
        download_folder_temp=download_folder_temp,
        finished=False,
        url=None,
        timeout=20
    )
    

    time.sleep(5)
    try:
        download.DownloadSetup()
    except (TimeoutException, NoSuchElementException):
        check_count = download.get_result_count()
        if check_count is None:
            zero_txt = os.path.join(download_folder, 'noresults.txt')
            if not os.path.exists(zero_txt):
                os.makedirs(zero_txt)
            print(f"Zero results to download for basin {basin_code}")
            logout_clearcookies(download)
            driver.close()
            return False  # Failed - no results

    # Main download process
    before = time.time()

    result_count = download.get_result_count()
    if result_count is None:
        logout_clearcookies(download)
        driver.close()
        return False  # Failed - no results

    # if result_count > 1000:
    #     print(f"Basin {basin_code} has {result_count} results (over 1000 limit). Skipping...")
    #     logout_clearcookies(download)
    #     driver.close()
    #     return False

    # if download.get_result_count() > 150000 and not getattr(search, 'already_switched_to_riparian', False):
    #     search.switch_to_riparian()
    #     search.already_switched_to_riparian = True  # Prevent re-switching
    #     search.search_process()
    #     download.DownloadSetup()

    consecutive_failures = 0
    failure_threshold = 3 # can raise or lower

    running=True
    # Get initial ranges for progress bar
    initial_ranges = download.get_ranges()
    total_ranges = len(initial_ranges)
    completed_ranges = set()
    
    success = False  # Track overall success

    # creae persisitent progress bar outside while loop
    with tqdm(total=total_ranges, desc=f"Overall Progress on {basin_code}") as pbar:

        while running:

            ranges_to_download = download.get_ranges()
        
            # Check if we're done
            if not ranges_to_download:
                print(f"All ranges for basin {basin_code} downloaded!")
                logout_clearcookies(download)
                driver.close()
                running = False
                success = True  # Mark as successful
                break
            
            print(f"Attempting to download {len(ranges_to_download)} ranges")

            for i, r in enumerate(ranges_to_download):
                try:
                    if i > 0: # if it's not the first loop
                        reset(download, login, search) # reset, which includes login, search, and setup
                    
                    download.check_clear_downloads(r)
                    try:
                        download.download_dialog(r)
                    except TimeoutException as te:
                        print(f"[ERROR] TimeoutException in download_dialog for range {r}: {te}")
                        # Save extra debug artifacts after timeout
                        try:
                            post_prefix = f"timeout_{basin_code}_{r}"
                            download.driver.save_screenshot(os.path.join(download_folder, f"{post_prefix}.png"))
                            with open(os.path.join(download_folder, f"{post_prefix}.html"), "w", encoding="utf-8") as f:
                                f.write(download.driver.page_source)
                        except Exception:
                            pass
                        raise  # let outer logic handle failures
                    except Exception as e:
                        print(f"[ERROR] Exception during download_dialog for range {r}: {e}")
                        # optionally save debug snapshot
                        try:
                            download.driver.save_screenshot(os.path.join(download_folder, f"err_{basin_code}_{r}.png"))
                        except Exception:
                            pass
                        raise
                    print(f"preparing to download range {r}")

                    download.wait_for_download()
                    download.move_file(r)

                    after = time.time()
                    elapsed = after - before

                    consecutive_failures = 0 # reset on success
                    print("Time elapsed since process began (minutes): ", elapsed/60)

                    # Update progress bar
                    if r not in completed_ranges:
                        completed_ranges.add(r)
                        if len(completed_ranges) <= total_ranges:
                            pbar.update(1)
                            if len(completed_ranges) == total_ranges:
                                print("All original ranges completed!")

                except DownloadFailedException:
                    consecutive_failures += 1
                    print(f"Download failed for range {r} after {consecutive_failures} consecutive failure(s)")
                    reset(download, login, search)
                    
                    # Check if we've hit the failure threshold
                    if consecutive_failures >= failure_threshold:
                        print(f"{basin_code} downloads failed {failure_threshold} times in a row, please try another basin")
                        logout_clearcookies(download)
                        driver.close()
                        running = False
                        success = False  # Mark as failed
                        break

                    continue  # Try the next range
                
                except Exception as e:
                    #print(f"Error occurred with range {r}: {e}")
                    continue  # Try next range
    
    return success  # Return whether download was successful