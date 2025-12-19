import requests
import re
import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup as bs
import time
import os
from io import StringIO
# ft

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
t1 = time.time()

def headless_browser():
    """ this function initiates the driver """    
    
    options = webdriver.ChromeOptions()
    
    options.add_argument("--headless")
    options.add_argument("--incognito")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    
#     to install the driver if not installed
#     driver = webdriver.Firefox(options=options)
    
#     to operate the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    return driver

def get_1_website():
    
    "last updated on 13 Jan 2024 "
    """MOHAWK MOUNTAIN:  https://www.mohawkmtn.com/"""
    
    res = requests.get("https://www.mohawkmtn.com/")
    soup = bs(res.text , "lxml")
    main_list = soup.select("div.condition-widget-wrapper")[0].select("ul")[0].select("li")
    
    try:
        
        trails_num_li = [li for li in main_list if ("trails" in li.text.lower()) and "open" in li.text.lower()][0]
        trails_num = trails_num_li.select("span.number-open")[0].text
    
    except:
        trails_num = "0"
        
    try:
        lifts_num_li = [li for li in main_list if ("lifts" in li.text.lower()) and "open" in li.text.lower()][0]
        lifts_num = lifts_num_li.select("span.number-open")[0].text
    
    except:
        lifts_num = "0"
    
        
    data_dict = {"MOHAWK MOUNTAIN" : {"trails" : int(trails_num) ,
                "lifts" : int(lifts_num)}}
        
    return data_dict

# ft
def get_2_website():
    """MOUNT SOUTHINGTON:  https://mountsouthington.com/trails-and-conditions/"""
    
    
    url = "https://mountsouthington.com/trails-and-conditions/"
    r = requests.get(url)
    soup = bs(r.text , "lxml")
    
    table = soup.select("div.overall-conditions")[0]
    all_data = [t.text for t in table.select("tr")]
    
    trails = int([d for d in all_data if "Trails Open:" in d][0].split("Trails Open:\n")[1].split("\n")[0].split("/")[0])
    lifts = int([d for d in all_data if "Lifts Open:" in d][0].split("Lifts Open:\n")[1].split("\n")[0].split("/")[0])
    try:
        depth = re.findall( "\d+" , [d for d in all_data if "Depth:" in d][0].split("Depth:\n")[1].split("\n")[0])[0]
    except:
        depth = 0
    
    data_dict = {"MOUNT SOUTHINGTON" : {"trails" : trails,
                "lifts" : lifts,
                "depth" : int(depth)}}
    
    return data_dict
# In[6]:

lists = ["MOHAWK MONTAIN" , "MOUNT SOUTHINGTON" , "POWDER RIDGE" , "SKI SUNDOWN" , "BIGROCK"]

def get_4_website():
    
    """SKI SUNDOWN:  https://skisundown.com/the-mountain/mountain-information/conditions-report/"""
    
    url = "https://skisundown.com/the-mountain/mountain-information/conditions-report/"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',}
    
    r = requests.get(url , headers = headers)
    soup = bs(r.text , "lxml")
    
    data_table = soup.select("div.row.conditions")[0]
    data_rows = [ d for p in data_table for d in p.text.split("\n") if d.strip() != ""]
    
    try:
        lifts = [l for l in data_rows if "Num. of Lifts Open:" in l][0].split("Num. of Lifts Open:")[1].strip("-'' ")
        lifts_num = int(lifts)
    except:
        lifts_num  = 0 
        
    try:
        trails = [t for t in data_rows if "Num. of Trails Open:" in t][0].split("Num. of Trails Open:")[1].strip("-'' ")
        trails_num = int(trails)
    except:
        trails_num = 0
    try:
        depth = int(re.findall("\d+" , [t for t in data_rows if "Base Snow:" in t][0].split("Base Snow:")[1])[0])
    except:
        depth = 0

    try:
        new_snow = re.findall("\d+" , [t for t in data_rows if "New Snow 24hrs:" in t][0].split("New Snow 24hrs:")[1])[0]
    except:
        new_snow = 0
    
    data_dict = {"SKI SUNDOWN" : {"trails" : trails_num ,
                 "lifts" : lifts_num ,
                 "depth" : depth,
                 "new snow" : new_snow}}
    
    return data_dict 


# ft
def flatten_lists(list_of_lists):
    final_list = []
    for sub_list in list_of_lists:
        final_list.extend(sub_list)
        
    return final_list


def get_6_website():
    """ BLACK MOUNTAIN ME: skiblackmountain.org/mountain-report """
    url = "https://skiblackmountain.org/mountain-report"
    
    r = requests.get(url)
    soup = bs(r.text , "lxml")
    tables = pd.read_html(StringIO(r.text))
    vals = [v for v in flatten_lists( tables[0].iloc[0: , :].values.tolist() ) if type(v) != type(np.nan)]

    try:
        new_snow = [v for v in vals if "Snowfall last 24 hours" in v][0].split("Snowfall last 24 hours:")[-1].strip('""')
    except:
        new_snow = ""
        
    try:
        depth = [v for v in vals if "Base Depth:" in v][0].split("Base Depth:")[-1].strip('""')
    except:
        depth = ""
        
      
    try:
        trails_num = int([v for v in vals if "Trails Open:" in v][0].split("Trails Open:")[-1].strip('""'))
    except:
        trails_num = 0 
        
    try:
        lifts_num = int([v for v in vals if "Lifts Open:" in v][0].split("Lifts Open:")[-1].strip('""'))
     
    except:
        lifts_num = 0
        
    trails_num = trails_num
        
    data_dict = {"BLACK MOUNTAIN ME" : {"lifts" : lifts_num ,
                                    "trails" : trails_num,
                                    "depth" : depth,
                                    "new snow" : new_snow}}
    return data_dict


def get_7_website():
    url = "https://camdensnowbowl.com/current-conditions/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    r = requests.get(url, headers=headers)
    soup = bs(r.text, "lxml")

    # -----------------------------
    # Extract ALL the <span class="number"> values
    # -----------------------------
    numbers = [n.get_text(strip=True) for n in soup.select("span.number")]

    snow_base = numbers[0] if len(numbers) > 0 else ""
    trails_open = numbers[1] if len(numbers) > 1 else ""
    lifts_open = numbers[2] if len(numbers) > 2 else ""

    # Clean quotes from snow base
    snow_base = snow_base.replace('"', "").strip()

    data_dict = {
        "CAMDEN SNOW BOWL": {
            "lifts": lifts_open,
            "trails": trails_open,
            "depth": snow_base
        }
    }

    return data_dict

def get_8_website():
    "last updated on 13 Jan 2024"
    """LOST VALLEY:  https://www.lostvalleyski.com/trails-conditions/"""
    
    url = "https://www.lostvalleyski.com/trails-conditions/"
    r = requests.get(url)
    soup = bs(r.text , "lxml")
    try:
        num_trails = soup.select('li.openDownHillTrails')[0].text
    except:
        num_trails= ""
        
    try:
        num_lifts = soup.select('li.openDownHillLifts')[0].text
        
    except:
        num_lifts = ""
        
    data_dict = {"LOST VALLEY" : {"trails" : num_trails,
                                 "lifts" : num_lifts}}
    return data_dict

def get_9_website():
    """
    Extracts ONLY the open values for:
    - Trails
    - Lifts
    - Uphill
    """

    url = "https://mtabram.com"
    r = requests.get(url)
    soup = bs(r.text, "lxml")

    # Select the 3 boxes that contain "open / total"
    boxes = soup.select("div.w-hwrapper")

    trails_open = lifts_open = uphill_open = None
    index = 0

    for box in boxes:
        nums = box.select("div.w-html")
        if len(nums) != 1 and len(nums) != 2:
            continue

        # OPEN VALUE is always the FIRST w-html
        open_val = nums[0].get_text(strip=True)

        try:
            open_val = int(open_val)
        except:
            continue

        if index == 0:      # Trails
            trails_open = open_val
        elif index == 1:    # Lifts
            lifts_open = open_val
        elif index == 2:    # Uphill
            uphill_open = open_val

        index += 1
        if index >= 3:
            break  # Done, we only need 3 boxes

    return {
        "MOUNT ABRAM": {
            "trails": trails_open,
            "lifts": lifts_open,
            "uphills": uphill_open
        }
    }

def get_10_website():
    "last updated on 16 dec 2023"
    """SADDLEBACK:  https://www.saddlebackmaine.com/mountain-report/"""
    
    driver = headless_browser()
    
    url = "https://www.saddlebackmaine.com/mountain-report/#overview"
    driver.get(url)
    time.sleep(10)
    soup = bs(driver.page_source , "lxml")

    lifts = soup.select("div#data-open-lifts-value")[0].text
    num_lifts = int(lifts.strip("\n \t").split("/")[0])

    trails = soup.select("div#data-open-trails-value")[0].text
    num_trails = int(trails.strip("\n \t").split("/")[0])

    temp =  soup.select("div#data-twenty-four-hour-snow-value")[0].text
    num_temp = int(temp.strip('"\n \t').split("/")[0])


    min_depth = soup.select("div#data-base-depth-value")[0].text
    num_min_depth = int(min_depth.replace("Base Depth Min" , "").strip('"\n\t ').split("/")[0])

    driver.quit()
    data_dict = {"SADDLEBACK" : {"lifts" : num_lifts,
                                "trails" : num_trails,
                                "new snow" : num_temp,
                                "depth" : num_min_depth}}
    return data_dict

# In[15]:


# ft
def get_11_website():
    """PLEASANT MOUNTAIN:  https://www.pleasantmountain.com/mountain-report"""
    
    url = "https://www.pleasantmountain.com/mountain-report"
    
    driver = headless_browser()
    
    # Load the page
    driver.get(url)
    time.sleep(5)  # Allow JavaScript to load the page
    
    # Parse the page source with BeautifulSoup
    soup = bs(driver.page_source, "lxml")
    driver.quit()
    
    # Find the "Lifts" and "Trails" elements
    elements = soup.select("ul.grid.grid-cols-1 li")
    
    lifts = 0
    trails = 0
    
    for element in elements:
        title = element.select_one("p.text-brwf-bodylg-sm, p.xl\\:text-brwf-bodylg-md")
        if title and title.text.strip() == "Lifts":
            lifts = int(element.select_one("span.h2").text.strip())
        elif title and title.text.strip() == "Trails":
            trails = int(element.select_one("span.h2").text.strip())
    
    # Construct the data dictionary
    data_dict = [{
        "PLEASANT MOUNTAIN": {
            "lifts": lifts,
            "trails": trails,
        }
    }]
    return data_dict


# In[16]:


# ft
def get_12_website():
    """SUGARLOAF:  https://www.sugarloaf.com/mountain-report"""
    
    url = "https://www.sugarloaf.com/mountain-report"

    driver = headless_browser()
    
    # Load the webpage
    driver.get(url)
    time.sleep(5)  # Wait for JavaScript to load the content
    
    # Locate the elements using Selenium
    elements = driver.find_elements(By.CSS_SELECTOR, "ul.hidden li")
    
    trails = 0
    lifts = 0
    
    for element in elements:
        # try:
            # Get the title (e.g., Trails, Lifts)
            title = element.find_element(By.CSS_SELECTOR, "p.text-brwf-bodylg-sm, p.xl\\:text-brwf-bodylg-md").text.strip()
            
            # Extract the numerator value
            numerator = int(element.find_element(By.CSS_SELECTOR, "span.h2").text.strip())
            
            if title == "Trails":
                trails = numerator
            elif title == "Lifts":
                lifts = numerator
        # except Exception as e:
        #     print(f"Error processing element: {e}")
    
    # Close the driver
    driver.quit()
    
    # Construct the data dictionary
    data_dict = {
        "SUGARLOAF": {
            "trails": trails,
            "lifts": lifts,
        }
    }
    
    return data_dict

# In[17]:


# ft
def get_13_website():
    """SUNDAY RIVER:  https://www.sundayriver.com/mountain-report"""
    
    url = "https://www.sundayriver.com/mountain-report"
    
    driver = headless_browser()
    
    # Load the page
    driver.get(url)
    time.sleep(5)  # Allow the JavaScript to load the content
    
    # Locate the elements
    elements = driver.find_elements(By.CSS_SELECTOR, "ul.hidden li")

    trails = 0
    lifts = 0

    for element in elements:
        # try:
            title = element.find_element(By.CSS_SELECTOR, "p.text-brwf-bodylg-sm, p.xl\\:text-brwf-bodylg-md").text.strip()
            numerator = int(element.find_element(By.CSS_SELECTOR, "span.h2").text.strip())
            
            if title == "Trails":
                trails = numerator
            elif title == "Lifts":
                lifts = numerator
        # except Exception as e:
        #     print(f"Error processing element: {e}")
    
    driver.quit()

    # Construct the data dictionary
    data_dict = {
        "SUNDAY RIVER": {
            "trails": trails,
            "lifts": lifts,
        }
    }
    
    return data_dict

# ft
def get_14_website():

    """BERKSHIRE EAST: https://berkshireeast.com/winter/mountain-conditions"""
    headers = {
        'authority': 'berkshireeast.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'dnt': '1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    url = "https://berkshireeast.com/winter/mountain-conditions"
    r = requests.get(url, headers=headers)
    soup = bs(r.text, "lxml")
    
    lifts_num = 0
    trails_num = 0
    
    try:
        # Extract lifts
        lifts_section = soup.select_one(".item_fields .col-06:has(.heading:contains('Lifts'))")
        if lifts_section:
            lifts_num = int(lifts_section.select_one(".stats").text.split("/")[0].strip())
    except:
        lifts_num = 0

    try:
        # Extract trails
        trails_section = soup.select_one(".item_fields .col-06:has(.heading:contains('Trails'))")
        if trails_section:
            trails_num = int(trails_section.select_one(".stats").text.split("/")[0].strip())
    except:
        trails_num = 0

    data_dict = {
        "BERKSHIRE EAST": {
            "trails": trails_num,
            "lifts": lifts_num,
            "depth": "",
            "new snow": ""
        }
    }

    return data_dict

def extract_items(container):
    """Generic extractor for lifts OR trails."""

    items = []
    open_count = 0

    # All Elementor rows are <section>
    sections = container.find_all("section", recursive=True)

    for sec in sections:
        name_tag = sec.select_one("h2.elementor-heading-title")
        # status_tag = sec.select_one("span.elementor-icon-list-text")
        cols = sec.select("div.elementor-inner-column")
        status_tag = cols[1].select_one("span.elementor-icon-list-text")

        # Skip headers or invalid rows
        if not name_tag or not status_tag:
            continue

        name = name_tag.get_text(strip=True)
        status = status_tag.get_text(strip=True).upper()

        # Skip header rows like "Status"
        if name.lower() == "status":
            continue

        items.append({"name": name, "status": status})

        if status == "OPEN":
            open_count += 1

    total = len(items)

    return items, open_count, total

def parse_trails(soup):
    trail_sections = soup.select("section.elementor-section.elementor-inner-section")

    trails = []
    open_count = 0

    for sec in trail_sections:
        cols = sec.select("div.elementor-inner-column")
        if len(cols) != 3:
            continue  # skip sections not matching the 3-column trail layout

        # --- Extract name ---
        name_tag = cols[0].select_one("h3.elementor-icon-box-title span")
        if not name_tag:
            continue
        name = name_tag.get_text(strip=True)

        # --- Extract status (only the visible one) ---
        status_div = cols[2].select_one(
            "div.elementor-element.elementor-icon-list--layout-traditional:not(.elementor-hidden-desktop):not(.elementor-hidden-tablet):not(.elementor-hidden-mobile)"
        )
        status_tag = status_div.select_one("span.elementor-icon-list-text")
        if not status_tag:
            continue

        status = status_tag.get_text(strip=True).upper()
        # print(f"{name}---->{status}")
        trails.append({
            "name": name,
            "status": status
        })

        if status == "OPEN":
            open_count += 1
    # print(trails)
    return trails, open_count, len(trails)

def get_15_website():
    URL = "https://bousquetmountain.com/lift-trail-status/"
    driver = headless_browser()
    driver.get(URL)
    wait = WebDriverWait(driver, 10)

    close_btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "a.dialog-close-button.dialog-lightbox-close-button")
    ))

    close_btn.click()
    time.sleep(1)
    soup = bs(driver.page_source, "lxml")

    # ---- LIFTS ----
    lift_container = soup.select_one('div[data-id="2056269"]')
    lifts, lifts_open, lifts_total = extract_items(lift_container)

    # ---- TRAILS ----
    trail_container = soup.select_one('div[data-id="9f1f1f4"]')
    trails, trails_open, trails_total = parse_trails(trail_container)

    # Remove carpets (trail list includes them)
    # trails = [t for t in trails if "carpet" not in t["name"].lower()]
    trails_open = sum(1 for t in trails if t["status"] == "OPEN")
    trails_total = len(trails)

    return {
        "BOUSQUET": {
            "lifts": lifts_open,
            # "lifts_total": lifts_total,
            # "lifts": lifts,
            "trails": trails_open,
            # "trails_total": trails_total,
            # "trails": trails,
        }
    }


def get_16_website():
    """CATAMOUNT: https://catamountski.com/winter/the-mountain/mountain-conditions"""

    url = "https://catamountski.com/winter/the-mountain/mountain-conditions"
    r = requests.get(url)
    soup = bs(r.text, "lxml")

    tables = soup.select("table.uk-table")

    # Safety check: need at least 2 tables
    if len(tables) < 2:
        return {"error": "Expected at least 2 tables"}

    # -----------------------
    # TABLE 1 → TRAILS
    # -----------------------
    trails = []
    open_trails = 0
    trail_rows = tables[1].select("tbody tr")

    for tr in trail_rows:
        name_tag = tr.select_one("td.fs-table-title .el-title")
        if not name_tag:
            continue
        name = name_tag.get_text(strip=True)

        status_td = tr.select_one("td.fs-table-text_2")
        icon = status_td.select_one("a.uk-icon") if status_td else None

        status = "OPEN" if icon and "color:green" in icon.get("style", "") else "CLOSED"
        trails.append({"name": name, "status": status})
        if status == "OPEN":
            open_trails += 1

    # -----------------------
    # TABLE 2 → LIFTS
    # -----------------------
    lifts = []
    open_lifts = 0
    lift_rows = tables[0].select("tbody tr")

    for tr in lift_rows:
        name_tag = tr.select_one("td.fs-table-title .el-title")
        if not name_tag:
            continue
        name = name_tag.get_text(strip=True)

        status_td = tr.select_one("td.fs-table-text_2")
        icon = status_td.select_one("a.uk-icon") if status_td else None

        status = "OPEN" if icon and "color:green" in icon.get("style", "") else "CLOSED"
        lifts.append({"name": name, "status": status})
        if status == "OPEN":
            open_lifts += 1

    # -----------------------
    # BUILD FINAL RESPONSE
    # -----------------------
    return {
        "CATAMOUNT": {
            "trails_open": open_trails,
            "trails_total": len(trails),
            "lifts_open": open_lifts,
            "lifts_total": len(lifts),
        }
    }



# In[21]:

def safe_int(val):
    """
    Safely convert lift/trail numbers to int.
    Returns 0 if the value is empty, missing, or non-numeric.
    """
    if not val:
        return 0
    val = val.strip()
    # Reject characters like — or other symbols
    if val in ["—", "-", "--", "N/A", "n/a"]:
        return 0
    # Extract first number only
    import re
    m = re.search(r"\d+", val)
    return int(m.group()) if m else 0

def get_17_website():

    url = "https://www.jiminypeak.com/The-Mountain/Mountain-Information/Snow-Report/"

    # Launch real Chrome to bypass Cloudflare fully
    driver = headless_browser()

    try:
        driver.get(url)

        # Wait for Cloudflare challenge + JS rendering
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.snow-report__stats-grid")))

        def tx(css):
            try:
                return driver.find_element(By.CSS_SELECTOR, css).text.strip()
            except:
                return ""

        depth = tx('[data-stat="depth"]')
        snowfall = tx('[data-stat="snowfall"]')
        lifts_day = tx('[data-stat="lifts-day"]')
        lifts_night = tx('[data-stat="lifts-night"]')
        trails_day = tx('[data-stat="trails-day"]')
        trails_night = tx('[data-stat="trails-night"]')

        data = {
            "JIMINY PEAK": {
                "depth": depth,                     
                "snowfall_24h": snowfall,
                "lifts_open_day": safe_int(lifts_day),
                "lifts_open_night": safe_int(lifts_night),
                "trails_open_day": safe_int(trails_day),
                "trails_open_night": safe_int(trails_night),
            }
        }

        return data

    finally:
        driver.quit()


def get_18_website():
    "last updated on 13 Jan 2024"
    """NASHOBA VALLEY:  https://skinashoba.com/snow_report/"""
    
    headers = {
        'authority': 'skinashoba.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
        
        
    url = "https://skinashoba.com/snow_report/"
    r = requests.get(url , headers = headers)
    soup = bs(r.text , "lxml")
    
    tables = pd.read_html(StringIO(r.text))
    
    trails_table = tables[2]
    trails_table.columns = trails_table.iloc[0 , :]
    trails_table = trails_table.iloc[1: , :]
    num_trails = np.sum([ 1 if "OPEN" in t else 0 for t in trails_table.Status.tolist()])
    
    lifts_table = tables[3]
    lifts_table.columns = lifts_table.iloc[0 , :]
    lifts_table = lifts_table.iloc[1 : , :]
    num_lifts = np.sum([ 1 if "OPEN" in t else 0 for t in lifts_table.dropna().Status.tolist()])
    
    orig_table = tables[0].set_index(0).T
    
    depth = int(orig_table["Base Depth"].tolist()[0].split("-")[0].strip('″"'))
    new_snow = int(orig_table["Recent Snowfall (24 hours)"].tolist()[0].strip('″"'))
    
    data_dict = {"NASHOBA VALLEY" : {"trails" : num_trails , 
                                    "lifts" : num_lifts,
                                    "depth" : depth,
                                    "new snow" : new_snow}}
    return data_dict


def get_19_website():
    """Extract trails and lifts from https://skibradford.com/snow-report/"""

    url = "https://skibradford.com/snow-report/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    r = requests.get(url, headers=headers, timeout=15)
    soup = bs(r.text, "lxml")

    # Default values
    trails = 0
    lifts = 0
    date = ""
    time = ""

    try:
        # Find all <p> rows inside the snowReportPage section
        report_section = soup.select_one("div.snowReportPage")
        rows = report_section.select("p")

        for row in rows:
            text = row.get_text(" ", strip=True)

            if text.startswith("Total Trails Open"):
                trails = int(text.split()[-1])

            if text.startswith("Total Lifts Open"):
                lifts = int(text.split()[-1])

            # if text.startswith("Date"):
            #     date = text.replace("Date", "").strip()

            # if text.startswith("Time"):
            #     time = text.replace("Time", "").strip()

    except Exception as e:
        print("Parsing error:", e)

    return {
        "BRADFORD": {
            # "date": date,
            # "time": time,
            "trails": trails,
            "lifts": lifts
        }
    }

def get_20_website():
    """BUTTERNUT: Extract Trails, Lifts, Depth, New Snow from table format"""

    url = "https://skibutternut.com/the-mountain/trails-conditions/condition-report"

    r = requests.get(url, timeout=15)
    soup = bs(r.text, "lxml")

    data = {
        "trails": 0,
        "lifts": 0,
        "depth": 0,
        "new snow": 0,
    }

    # Select all <tr> rows in the ski-report-table
    rows = soup.select("table.ski-report-table tbody tr")

    for row in rows:
        cells = row.select("td")
        if len(cells) < 2:
            continue

        category = cells[0].get_text(" ", strip=True)
        value = cells[1].get_text(" ", strip=True)

        # --- Extract New Snow ---
        if "New Snow" in category:
            # remove quotes like 0"
            num = re.findall(r"\d+", value)
            data["new snow"] = int(num[0]) if num else 0

        # --- Extract Open Trails ---
        if "Open Trails" in category:
            num = re.findall(r"\d+", value)
            data["trails"] = int(num[0]) if num else 0

        # --- Extract Open Lifts ---
        if "Open Lifts" in category:
            num = re.findall(r"\d+", value)
            data["lifts"] = int(num[0]) if num else 0

        # --- Extract Base Depth ---
        if "Base Depth" in category:
            # value example: 18-24"
            nums = re.findall(r"\d+", value)
            if nums:
                data["depth"] = int(nums[0])  # lower bound of depth

    return {"BUTTERNUT": data}

# ft
def get_21_website():
    "last updated on 16 dec 2023"
    """SKI WARD:  https://www.skiward.com/mountain-info/snow-report/"""
    
    url = "https://skiward.com/mountain-info/conditions/"
    r = requests.get(url)
    soup = bs(r.text , "lxml")
    all_lines = str(soup.select("#post-63 > div > div > div.vc_row.wpb_row.vc_row-fluid.narrow > div.wpb_column.vc_column_container.vc_col-sm-8 > div > div > div:nth-child(2) > div")[0]).split("<br/>")
    all_texts = [ bs(line , "lxml").text for line in all_lines]
    
    trails = [t for t in all_texts if "Open Terrain" in t][0].strip("\n\t ''").replace("Open Terrain" , "").replace("\n" , " ")
    try:
        trails_num = re.findall("(\d+) of (\d+) trails" , trails)[0][0]
    except:
        trails_num = ""
        
        
    depth = [t for t in all_texts if "Average Base Depth" in t][0].strip("\n\t ''").replace("\n" , " ").replace("Average Base Depth" , "")
    try:
        depth_num = re.findall("(\d+)″ – (\d+)″" , depth)[0][0]
    except:
        depth_num = ""
        
        
    lifts = [t for t in all_texts if "Lifts Open" in t][0].strip("\n\t ''").replace("Lifts Open" , "").replace("\n" , " ")
    try:
        lifts_num = re.findall("(\d+) of (\d+) lifts" , lifts)[0][0]
    except:
        lifts_num = ""
        
        
        
    
    data_dict = {"SKI WARD" : {"trails" : trails_num,
                              "lifts" : lifts_num , 
                              "depth" : depth_num}}
        
    return data_dict

# ft
def get_22_website():
    
    """WACHUSETT:  https://www.wachusett.com/The-Mountain/Your-Visit/Snow-Report.aspx"""
    
    headers = {
        'authority': 'wp-api.wachusett.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'dnt': '1',
        'origin': 'https://www.wachusett.com',
        'referer': 'https://www.wachusett.com/',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    
    response = requests.get('https://wp-api.wachusett.com/api/SnowReport/Status', headers=headers)
    j = json.loads(response.text)
    num_lifts = np.sum([l['Status']["Open"]  for l in j["Lifts"]])
    num_trails = np.sum([l['Status']["Open"]  for l in j["Trails"]])
    depth = j["Report"]["DepthMin"]
    new_snow = j["Report"]["NewSnow"]
    
    data_dict = {"WACHUSETT" : { "trails" : num_trails , 
                               "lifts" : num_lifts,
                               "depth" : depth,
                               "new snow" : new_snow}}
    return data_dict


# In[27]:


# ft
def get_23_website():
    
    """ATTITASH:  https://www.attitash.com/the-mountain/mountain-conditions/snow-and-weather-report.aspx"""
    
    url = "https://www.attitash.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx"
    r = requests.get(url)
    soup = bs(r.text , "lxml")
        
    num_lifts = int(soup.select("div[data-terrain-status-id='lifts']")[0].select("div.terrain_summary__circle")[0].get("data-open"))
    num_trails = int(soup.select("div[data-terrain-status-id='runs']")[0].select("div.terrain_summary__circle")[0].get("data-open"))
    
        
    url2 = 'https://www.attitash.com/api/PageApi/GetWeatherDataForHeader'
    r2 = requests.get(url2)
    soup2 = bs(r2.text , "lxml")
    
    j = json.loads(r2.text)
    new_snow = int(j["SnowReportSections"][0]['Depth']['Inches'])
    depth = int(j["SnowReportSections"][-1]['Depth']['Inches'])

    data_dict = {"ATTITASH" : {"trails" : num_trails,
                              "lifts" : num_lifts,
                              "depth" : depth,
                              "new snow" : new_snow}}
    return data_dict


def get_24_website():
    """BRETTON WOODS: https://www.brettonwoods.com/snow-trail-report/"""

    url = "https://www.brettonwoods.com/snow-trail-report/"
    r = requests.get(url)
    soup = bs(r.text, "lxml")

    # ----------------------------------------------------
    # Extract Trails and Lifts
    # ----------------------------------------------------
    summary_items = soup.select("div.trail-reports__summary-item")

    num_trails = 0
    num_lifts = 0

    for item in summary_items:
        heading = item.select_one(".trail-reports__summary-item-heading").get_text(strip=True)
        count_text = item.select_one(".trail-reports__summary-item-count").get_text(strip=True)

        if heading == "Trail Count":
            num_trails = int(count_text.split("/")[0])

        if heading == "Lifts Open":
            num_lifts = int(count_text.split("/")[0])

    # ----------------------------------------------------
    # Extract Recent Snowfall (Mountain Base recent value)
    # ----------------------------------------------------
    new_snow = 0
    snowfall_rows = soup.select("div.trail-reports__snowfall-row")

    for row in snowfall_rows:
        cells = row.select("div.trail-reports__snowfall-cell")
        if not cells:
            continue
        
        label = cells[0].get_text(strip=True)

        if label == "Recent":
            value = cells[1].get_text(strip=True)  # Mountain Base recent
            nums = re.findall(r"\d+", value)
            new_snow = int(nums[0]) if nums else 0
            break

    return {
        "BRETTON WOODS": {
            "trails": num_trails,
            "lifts": num_lifts,
            "new snow": new_snow
        }
    }

def get_25_website():
    """BLACK MOUNTAIN NH – https://www.blackmt.com/conditions"""

    url = "https://www.blackmt.com/conditions"
    r = requests.get(url, timeout=15)
    soup = bs(r.text, "lxml")

    # All <p> elements that contain condition text
    ps = soup.select("p.font_8.wixui-rich-text__text")

    trails = 0
    lifts = 0
    snow_24h = 0

    for p in ps:
        text = p.get_text(" ", strip=True)

        # ---- Trails Open ----
        if "Trails Open" in text:
            nums = re.findall(r"\d+", text)
            trails = int(nums[0]) if nums else 0

        # ---- Lifts Open ----
        if "Lifts Open" in text:
            nums = re.findall(r"\d+", text)
            lifts = int(nums[0]) if nums else 0

        # ---- 24-hour Snow Total ----
        if "24-hour Snow Total" in text:
            nums = re.findall(r"\d+", text)
            snow_24h = int(nums[0]) if nums else 0

    data_dict = {
        "BLACK MOUNTAIN NH": {
            "trails": trails,
            "lifts": lifts,
            "new snow": snow_24h
        }
    }

    return data_dict



lls = ["MOHAWK MOUNTAIN" , "MOUNT SOUTHINGTON" ,"POWDER RIDGE" ,  "SKI SUNDOWN"  , "BIGROCK" , "BLACK MOUNTAIN NH" , "CAMDEN SNOW BOWL" , "LOST VALLEY", 
       "MOUNT ABRAM" , "SADDLEBACK" , "PLEASANT MOUNTAIN" , "SUGARLOAF" , "SUNDAY RIVER" , "BERKSHIRE EAST" , "BOUSQUET"  , "CATAMOUNT"  ,"JIMINY PEAK" , 
       "NASHOBA VALLEY"  , "BRADFORD" , "BUTTERNUT"  , "SKI WARD" , "WACHUSETT" , "ATTITASH"  , "BRETTON WOODS" , "CANNON MOUNTAIN" ,"CRANMORE" ,  "CROTCHED"]
# In[30]:


# ft
def get_26_website():
    """CANNON MOUNTAIN – https://www.cannonmt.com/mountain-report"""

    url = "https://www.cannonmt.com/mountain-report"
    r = requests.get(url, timeout=15)
    soup = bs(r.text, "lxml")

    snowfall = 0
    trails = 0
    lifts = 0

    # Get all metric blocks inside this section
    blocks = soup.select("section.bg-backgroundSecondary div.lg\\:p-4")

    for block in blocks:
        label_tag = block.select_one(".label")
        value_tag = block.select_one(".font-swiss-outline")

        if not label_tag or not value_tag:
            continue

        label = label_tag.get_text(strip=True).upper()
        value = value_tag.get_text(strip=True)

        # ---- SNOWFALL TO DATE ----
        if "SNOWFALL TO DATE" in label:
            nums = re.findall(r"\d+", value)
            snowfall = int(nums[0]) if nums else 0

        # ---- OPEN TRAILS ----
        elif "OPEN TRAILS" in label:
            nums = re.findall(r"\d+", value)
            trails = int(nums[0]) if nums else 0

        # ---- OPEN LIFTS ----
        elif "OPEN LIFTS" in label:
            nums = re.findall(r"\d+", value)
            lifts = int(nums[0]) if nums else 0

    data_dict = {
        "CANNON MOUNTAIN": {
            "trails": trails,
            "lifts": lifts,
            "new snow": snowfall
        }
    }

    return data_dict

def get_27_website():
    """CRANMORE – https://www.cranmore.com/Snow-Report"""

    url = "https://www.cranmore.com/Snow-Report"
    response = requests.get(url, timeout=15)
    soup = bs(response.text, "lxml")

    datapoints = soup.select("div.conditions div.datapoint")

    trails = 0
    lifts = 0
    depth = 0
    snow_24h = 0

    for dp in datapoints:
        title_el = dp.select_one("h3")
        value_el = dp.select_one("span.value")

        if not title_el or not value_el:
            continue

        title = title_el.get_text(strip=True)
        value = value_el.get_text(strip=True)

        # ---- Open Lifts ----
        if title == "Open Lifts":
            nums = re.findall(r"\d+", value)
            lifts = int(nums[0]) if nums else 0

        # ---- Open Trails ----
        elif title == "Open Trails":
            nums = re.findall(r"\d+", value)
            trails = int(nums[0]) if nums else 0

        # ---- Base Depth ----
        elif title == "Base Depth":
            nums = re.findall(r"\d+", value)
            depth = int(nums[0]) if nums else 0  # lower bound only

        # ---- 24 Hour Total ----
        elif title == "24 Hour Total":
            nums = re.findall(r"\d+", value)
            snow_24h = int(nums[0]) if nums else 0

    return {
        "CRANMORE": {
            "trails": trails,
            "lifts": lifts,
            "depth": depth,
            "new snow": snow_24h
        }
    }
        

def get_28_website():
    """CROTCHED: lift & trail counts + snow data"""

    # ---- 1. SCRAPE LIFTS & TRAILS FROM HTML ----
    url_status = "https://www.crotchedmtn.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx"
    r = requests.get(url_status, timeout=15)
    soup = bs(r.text, "lxml")

    # Select the containers using new structure
    lifts_block = soup.select_one("div.terrain_summary__tab_main[data-terrain-status-id='lifts']")
    runs_block  = soup.select_one("div.terrain_summary__tab_main[data-terrain-status-id='runs']")

    # Extract numeric values
    num_lifts = 0
    num_trails = 0

    # Extract lifts
    if lifts_block:
        circle = lifts_block.select_one("div.terrain_summary__circle")
        if circle:
            num_lifts = int(circle.get("data-open", 0))

    # Extract trails
    if runs_block:
        circle = runs_block.select_one("div.terrain_summary__circle")
        if circle:
            num_trails = int(circle.get("data-open", 0))

    # ---- 2. SCRAPE DEPTH + NEW SNOW FROM API ----
    api_url = "https://www.crotchedmtn.com/api/PageApi/GetWeatherDataForHeader"
    params = {"_": "1671547080977"}

    j = requests.get(api_url, params=params, timeout=15).json()

    try:
        new_snow = int(j["SnowReportSections"][0]['Depth']['Inches'])
    except:
        new_snow = 0

    try:
        depth = int(j["SnowReportSections"][-1]['Depth']['Inches'])
    except:
        depth = 0

    # ---- 3. RETURN CLEAN DICTIONARY ----
    return {
        "CROTCHED": {
            "trails": num_trails,
            "lifts": num_lifts,
            "depth": depth,
            "new snow": new_snow
        }
    }

# ft
def get_29_website():
    """DARTMOUTH SKIWAY:  https://sites.dartmouth.edu/skiway/mountain/ (LIFTS ONLY)"""
    
    headers = {
        'authority': 'www.snocountry.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'dnt': '1',
        'referer': 'https://sites.dartmouth.edu/',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'object',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    
    params = {
        'code': 'vr-603008',
        'state': 'nh',
        'type': 'NA_Alpine',
        'region': 'us',
        'pettabs': '3',
        'size': 'xsmall',
        'color': 'white',
        'noads': 'no',
    }
    
    response = requests.get('https://www.snocountry.com/widget/widget_resort.php', params=params , headers = headers)
    tables = pd.read_html(StringIO(response.text))
    
    df = tables[0]
    df.columns = df.iloc[1 , :]
    df = df.iloc[2:3  ,:]
    
    try:
        num_lifts = int(df["Lifts Open"].tolist()[0].split("of")[0].strip())
    except:
        num_lifts = 0
        
    try:
        num_trails = int(df["Trails Open"].tolist()[0].split("of")[0].strip())
    except:
        num_trails = 0
        
    try:
        new_snow = int(df["24 Hour"].tolist()[0].strip('""'))
    except:
        new_snow = 0
        
    data_dict = {"DARTMOUTH SKIWAY" : {"lifts" : num_lifts,
                                      "trails" : num_trails,
                                      "new snow" : new_snow}}
    
    
    
    return data_dict 



# In[34]:


# ft
def get_30_website():
    url = "https://www.kingpine.com/snow-report-conditions"

    browser = headless_browser()

    browser.get(url)
    time.sleep(2)   # allow iframe to load

    # --- Find the iframe with ID iFrameResizer0 ---
    try:
        iframe = browser.find_element("css selector", "iframe#iframeResizer0, iframe#iFrameResizer0")
    except Exception:
        print("❌ iframe NOT found")
        browser.quit()
        return

    # Switch selenium to the iframe DOM
    browser.switch_to.frame(iframe)
    time.sleep(1)

    # NOW get the dynamic HTML inside iframe
    html = browser.page_source
    soup = bs(html, "lxml")

    # --- Extract Trails ---
    trails_dl = soup.find("dt", string=lambda x: x and "Trails Open" in x)
    trails_val = trails_dl.find_next("dd").text.strip().split()[0]
    trails = int(trails_val)

    # --- Extract Lifts ---
    lifts_dl = soup.find("dt", string=lambda x: x and "Lifts Open" in x)
    lifts_val = lifts_dl.find_next("dd").text.strip().split()[0]
    lifts = int(lifts_val)

    # --- Extract Base Depth ---
    base_dl = soup.find("dt", string=lambda x: x and "Base Depth" in x)
    base_raw = base_dl.find_next("dd").text
    base = int(re.findall(r"\d+", base_raw)[0])

    # --- Extract New Snow 24h ---
    snow_dl = soup.find("dt", string=lambda x: x and "24 Hour" in x)
    snow_raw = snow_dl.find_next("dd").text
    new_snow = int(re.findall(r"\d+", snow_raw)[0])

    browser.quit()

    return {
        "KING PINE": {
            "trails": trails,
            "lifts": lifts,
            "depth": base,
            "new snow": new_snow
        }
    }

# In[35]:


# ft
def get_31_website():
    """MOUNT SUNAPEE:  https://www.mountsunapee.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx"""
    
    r = requests.get("https://www.mountsunapee.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx")
    soup = bs(r.text , "lxml")
    
        
    num_lifts = int(soup.select("div[data-terrain-status-id='lifts']")[0].select("div.terrain_summary__circle")[0].get("data-open"))
    num_trails = int(soup.select("div[data-terrain-status-id='runs']")[0].select("div.terrain_summary__circle")[0].get("data-open"))
    
    r = requests.get("https://www.mountsunapee.com/the-mountain/mountain-conditions/snow-and-weather-report.aspx")
    soup = bs(r.text , "lxml")
    script = str(soup.select("#body-content > div > div:nth-child(2) > div.weather_detail.container-fluid > div:nth-child(1) > div > script:nth-child(3)")[0])
    
    try:
        new_snow = int(re.findall('"TwentyFourHourSnowfall":{"Inches":"(.*?)","Centimeters":"(.*?)"},' , script)[0][1])
    except:
        new_snow = 0
        
    depth = int(re.findall('"BaseDepth":{"Inches":"(.*?)","Centimeters":"(.*?)"},' , script)[0][1])
    
    data_dict = {"MOUNT SUNAPEE" : {"trails" : num_trails , 
                                   "lifts" : num_lifts,
                                   "depth" : depth,
                                   "new snow" : new_snow}}
    
    
    return data_dict

def get_32_website():
    """PATS PEAK:  https://www.patspeak.com/the-mountain/mountain-info/snow-report/"""
    
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://www.patspeak.com/the-mountain/mountain-info/snow-report/")
    time.sleep(10)

    soup = bs(driver.page_source, "lxml")

    # ---- Extract Trails ----
    try:
        num_trails = int(soup.select_one("#trails-open").text.strip())
    except:
        num_trails = 0

    # ---- Extract Lifts ----
    try:
        num_lifts = int(soup.select_one("#lifts-open").text.strip())
    except:
        num_lifts = 0

    # ---- Extract Base Depth ----
    try:
        depth_str = soup.select_one("#base-depth").text.strip()  # e.g. 6"—18"
        depth = depth_str
    except:
        depth = None

    # ---- Extract New Snow Past 24 Hours ----
    try:
        new_snow_str = soup.select_one("#new-snow-in-last-24-hours").text.strip()  # e.g. 0"
        new_snow = int(re.findall(r"\d+", new_snow_str)[0])
    except:
        new_snow = None

    data_dict = {
        "PATS PEAK": {
            "trails": num_trails,
            "lifts": num_lifts,
            "depth": depth,
            "new snow": new_snow
        }
    }

    return data_dict

def get_33_website():
    "last updated 16 dec 2023"
    """RAGGED MOUNTAIN: https://raggedmountainresort.com/Slopes/"""
    
    
    headers = {
        'authority': 'www.raggedmountainresort.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'dnt': '1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
        
    url = "https://www.raggedmountainresort.com/mountain-report-cams/"
    r = requests.get(url , headers = headers)
    soup = bs(r.text , "lxml")
    
    all_data = soup.select("div.snow-text")
    
    num_trails = soup.select("div.slopes-details")[0].select("div.content")[0].select("h4")[0].text.strip().split(" ")[0]
    num_lifts = sum([ 1 if status.lower() == "open" else 0 for status in pd.read_html(StringIO(str(soup.select("div.lift-name")[0])))[0]["Status"].tolist()])
    
    
    depth = [cond.text.strip(" ''\n\t”") for cond in all_data if "Current Base" in cond.text][0].replace("Current Base" , "").strip(" ''\n\t”").split("-")[0]
    new_snow = [cond.text.strip("\n ''\n\t”") for cond in all_data if "Last 24 hrs." in cond.text][0].replace("Last 24 hrs." , "").strip(" ''\n\t”")
    
    data_dict = {"RAGGED MOUNTAIN" : {"trails" : num_trails , 
                                     "lifts" : num_lifts,
                                     "depth" : depth , 
                                     "new snow" : new_snow}}
    
    
    return data_dict

def get_34_website():
    """WATERVILLE VALLEY: https://www.waterville.com/snow-report-maps"""

    url = "https://www.waterville.com/snow-report-maps"

    browser = headless_browser()
    browser.get(url)
    time.sleep(5)

    # --- FIND THE IFRAME ---
    try:
        iframe = browser.find_element("css selector", "iframe#iFrameResizer1, iframe#iFrameResizer1")
    except:
        print("❌ iframe NOT found")
        browser.quit()
        return {}
    # --- SWITCH INTO IFRAME ---
    browser.switch_to.frame(iframe)
    time.sleep(1)

    html = browser.page_source
    browser.quit()

    soup = bs(html, "lxml")
    container = soup.select_one("#snow-cond")
    if not container:
        return {"ERROR": "snow-cond NOT FOUND"}
    # -------------------------
    # New Snow (Past 24 Hours)
    # -------------------------
    try:
        dt = container.find("dt", string=lambda x: x and "Past 24 Hours" in x)
        dd = dt.find_next("dd").get_text(strip=True)
        nums = re.findall(r"\d+", dd)
        new_snow = int(nums[0]) if nums else 0
    except:
        new_snow = 0

    # -------------------------
    # Base Depth
    # -------------------------
    try:
        dt = container.find("dt", string=lambda x: x and "Base Depth" in x)
        dd = dt.find_next("dd").get_text(strip=True)
        nums = re.findall(r"\d+", dd)
        depth = f"{nums[0]}-{nums[1]}" if len(nums) >= 2 else nums[0]
    except:
        depth = None

    # -------------------------
    # Open Lifts
    # -------------------------
    try:
        dt = container.find("dt", string=lambda x: x and "Open Lifts" in x)
        dd = dt.find_next("dd").get_text(strip=True)
        lifts_open = int(re.findall(r"\d+", dd)[0])
    except:
        lifts_open = 0

    # -------------------------
    # Open Trails
    # -------------------------
    try:
        dt = container.find("dt", string=lambda x: x and "Open Trails" in x)
        dd = dt.find_next("dd").get_text(strip=True)
        trails_open = int(re.findall(r"\d+", dd)[0])
    except:
        trails_open = 0
    return {
        "WATERVILLE VALLEY": {
            "trails": trails_open,
            "lifts": lifts_open,
            "depth": depth,
            "new snow": new_snow,
        }
    }


def get_35_website():
    
    "last updated on 18 Jan 2024"
    """WHALEBACK:  https://www.whaleback.com/trail-report"""

    driver = headless_browser()
    

    driver.get("https://www.whaleback.com/trail-report")
    time.sleep(8)

    # -------------------------------
    # Step 1: Enter FIRST iframe
    # -------------------------------
    iframes_lvl1 = driver.find_elements(By.TAG_NAME, "iframe")

    first_iframe = iframes_lvl1[1]
    driver.switch_to.frame(first_iframe)
    time.sleep(2)

    # -------------------------------
    # Step 2: Enter SECOND iframe
    # -------------------------------
    iframes_lvl2 = driver.find_elements(By.TAG_NAME, "iframe")
    second_iframe = iframes_lvl2[-1]

    driver.switch_to.frame(second_iframe)
    time.sleep(2)

    tables = pd.read_html(StringIO(driver.page_source))

    df = tables[0]
    df = df.fillna("")

    # Google Sheet sometimes has 5 columns → keep first 3 only
    df = df.iloc[:, :3]
    df.columns = ["un", "label", "value"]

    def get_value(label):
        row = df[df["label"].str.contains(label, na=False)]
        if row.empty:
            return ""
        return row["value"].iloc[0].strip()

    # Lifts
    try:
        lifts_raw = get_value("Lifts Open:")
        lifts = int(re.findall(r"\d+", lifts_raw)[0]) if lifts_raw else 0
    except:
        lifts = 0

    # Trails
    try:
        trails_raw = get_value("Trails Open:")
        trails = int(re.findall(r"\d+", trails_raw)[0]) if trails_raw else 0
    except:
        trails = 0

    # Base depth
    try:
        base_raw = get_value("Base:")
        nums = re.findall(r"\d+", base_raw)
        depth = int(nums[0]) if nums else 0
    except:
        depth = 0

    # New Snow
    try:
        snow_raw = get_value("New Snow In The Last 24 Hours:")
        nums = re.findall(r"\d+", snow_raw)
        new_snow = int(nums[0]) if nums else 0
    except:
        new_snow = 0

    data_dict = {
        "WHALEBACK": {
            "trails": trails,
            "lifts": lifts,
            "depth": depth,
            "new snow": new_snow,
        }
    }

    return data_dict

# ft
def get_36_website():
    """WILDCAT:  https://www.skiwildcat.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx"""
    
    url = "https://www.skiwildcat.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx"
    r = requests.get(url)
    soup = bs(r.text , "lxml")
        
    num_lifts = int(soup.select("div[data-terrain-status-id='lifts']")[0].select("div.terrain_summary__circle")[0].get("data-open"))
    num_trails = int(soup.select("div[data-terrain-status-id='runs']")[0].select("div.terrain_summary__circle")[0].get("data-open"))
    
        
    url2 = 'https://www.skiwildcat.com/api/PageApi/GetWeatherDataForHeader'
    r2 = requests.get(url2)
    soup2 = bs(r2.text , "lxml")
    
    j = json.loads(r2.text)
    new_snow = int(j["SnowReportSections"][0]['Depth']['Inches'])
    depth = int(j["SnowReportSections"][-1]['Depth']['Inches'])
    
    data_dict = {"WILDCAT" : {"trails" : num_trails , 
                             "lifts" : num_lifts,
                             "depth" : depth,
                             "new snow" : new_snow}}
    
    return data_dict


# In[41]:


# ft
def get_37_website():

    """YAWGOO VALLEY:  https://yawgoo.com/winter/report/"""
    
    url = "https://yawgoo.com/winter/report/"
    r = requests.get(url)
    soup = bs(r.text , "lxml")
    
    all_lists = [l.text.strip() for l in soup.select("ul.uabb-info-list-wrapper.uabb-info-list-left > li")]
    
    lifts_list = [ 0 if "closed" in t.lower() else 1 for t in [l for l in all_lists if "lift" in l.lower()]]
    num_lifts = np.sum(lifts_list)
    
    trails_list = [ 0 if "closed" in t.lower() else 1 for t in [l for l in all_lists if "lift" not in l.lower()]]
    num_trails = np.sum(trails_list)
    
    data_dict = {"YAWGOO VALLEY" : {"trails" : num_trails , 
                                   "lifts" : num_lifts}}
    
    
    return data_dict


def get_38_website():

    url = "https://www.boltonvalley.com/winter/trail-maps-snow-reports/snow-reports/"

    browser = headless_browser()

    browser.get(url)
    time.sleep(2)

    # --- FIND THE IFRAME ---
    try:
        iframe = browser.find_element("css selector", "iframe#iframeResizer0, iframe#iFrameResizer0")
    except:
        print("❌ iframe NOT found")
        browser.quit()
        return {}

    # --- SWITCH INTO IFRAME ---
    browser.switch_to.frame(iframe)
    time.sleep(1)

    # --- PARSE HTML ---
    html = browser.page_source
    soup = bs(html, "lxml")

    # ====== SNOW FALL SECTION ======
    snow_section = soup.select_one("section.SnowReport-section.snowfall")
    snow_measures = snow_section.select("dl.SnowReport-measure")

    try:
        snow_new = re.findall(
            r"\d+",
            next(m.dd.text for m in snow_measures if "Last 24 Hours" in m.dt.text)
        )[0]
    except:
        snow_new = ""

    # ====== CONDITIONS SECTION ======
    cond_section = soup.select_one("section.SnowReport-section.conditions")

    # LIFTS + TRAILS
    lt_measures = cond_section.select_one("div.OpenLiftsTrails").select("dl.SnowReport-measure")

    lifts = next(m.dd.text for m in lt_measures if "Lifts" in m.dt.text)
    trails = next(m.dd.text for m in lt_measures if "Trails" in m.dt.text)

    # BASE DEPTH
    cond_measures = cond_section.select("div.SnowConditions dl.SnowReport-measure")

    try:
        depth_raw = next(m.dd.text for m in cond_measures if "Base Depth" in m.dt.text)
        depth = re.findall(r"\d+", depth_raw)[0]
    except:
        depth = ""

    browser.quit()

    # BUILD RESULT
    data_dict = {
        "BOLTON VALLEY": {
            "trails": trails,
            "lifts": lifts,
            "depth": depth,
            "new snow": snow_new
        }
    }

    return data_dict


# ft
def get_39_website():
    """BROMLEY:  https://www.bromley.com/snow-report/"""
    
    url = "https://www.bromley.com/snow-report/"
    r = requests.get(url)
    soup = bs(r.text, "lxml")
    
    try:
        # Extract Trails Open
        trails_section = soup.find("h5", string="Trails Open")
        trails_text = trails_section.find_next("h1").text.strip()
        num_trails = int(trails_text.split()[0])
    except Exception:
        num_trails = 0
    
    try:
        # Extract Lifts Open
        lifts_section = soup.find("h5", string="Lifts Open")
        lifts_text = lifts_section.find_next("h1").text.strip()
        num_lifts = int(lifts_text.split()[0])
    except Exception:
        num_lifts = 0

    try:
        # Extract Base Depth
        depth_section = soup.find("h5", string="Base Depth")
        depth_text = depth_section.find_next("h1").text.strip()
        depth = int(depth_text.split('"')[0])
    except Exception:
        depth = 0
    
    try:
        # Extract New Snow
        new_snow_section = soup.find("h5", string="New Snow")
        new_snow_text = new_snow_section.find_next("h1").text.strip()
        new_snow = float(new_snow_text.split('"')[0])
    except Exception:
        new_snow = 0.0
    
    data_dict = {
        "BROMLEY": {
            "trails": num_trails,
            "lifts": num_lifts,
            "depth": depth,
            "new snow": new_snow
        }
    }
    
    return data_dict
# In[44]:


# ft
def get_40_website():
    import requests
    from bs4 import BeautifulSoup as bs

    url = "https://skiburke.com/the-mountain/weather-conditions#lifts"
    r = requests.get(url)
    soup = bs(r.text, "lxml")

    # ---------------------------------------------
    # 1️⃣ SNOWFALL — extract 24 hours
    # ---------------------------------------------
    snowfall_rows = soup.select("table.uk-table tbody tr")

    snowfall_24h = ""
    for row in snowfall_rows:
        title = row.select_one("td .el-title")
        value = row.select_one("td .el-text_1")
        if title and value and "24 Hours" in title.text:
            snowfall_24h = value.text.strip().replace('"', "")
            break

    # ---------------------------------------------
    # 2️⃣ LIFT STATUS (open lifts)
    # ---------------------------------------------
    lift_rows = soup.select("table.uk-table-divider tbody tr")

    open_lifts = 0
    closed_lifts = 0

    for tr in lift_rows:
        td_open = tr.select_one("td:nth-child(2) span.uk-text-success")
        td_closed = tr.select_one("td:nth-child(3) span.uk-text-danger")

        if td_open:
            open_lifts += 1
        elif td_closed:
            closed_lifts += 1

    # ---------------------------------------------
    # 3️⃣ TRAIL STATUS (open trails)
    #     Two separate tables → count both
    # ---------------------------------------------
    trail_rows = soup.select("table.uk-table.uk-table-divider tbody.fs-load-more-container tr")

    open_trails = 0

    for tr in trail_rows:
        # Green = open → span.uk-text-success
        is_open = tr.select_one("td:nth-child(3) span.uk-text-success")
        if is_open:
            open_trails += 1

    # ---------------------------------------------
    # 4️⃣ Final Output
    # ---------------------------------------------
    return {
        "BURKE": {
            "snow_24h": snowfall_24h,
            "lifts": open_lifts,
            "trails": open_trails
        }
    }




# In[45]:


# ft
def get_41_website():
    url = "https://jaypeakresort.com/skiing-riding/snow-report-maps/snow-report"


    browser = headless_browser()

    browser.get(url)
    time.sleep(3)

    # --- Find the iframe with ID iFrameResizer0 ---
    try:
        iframe = browser.find_element("css selector", "iframe#iframeResizer0, iframe#iFrameResizer0")
    except Exception:
        print("❌ iframe NOT found")
        browser.quit()
        return


    # Switch selenium to the iframe DOM
    browser.switch_to.frame(iframe)
    time.sleep(1)

    # --- Now inside iframe — get HTML ---
    html = browser.page_source
    soup = bs(html, "lxml")

    browser.quit()
    container = soup.select_one("#snow-cond")
    if not container:
        return {"ERROR": "snow-cond NOT FOUND"}
    # --- Extract all SnowReport-measure entries ---
    measures = container.select("dl.SnowReport-measure")

    def get_value(label):
        for dl in measures:
            dt = dl.select_one("dt")
            dd = dl.select_one("dd")
            if dt and dd and label.lower() in dt.text.lower():
                return dd.text.strip()
        return ""

    # 1️⃣ New Snow (24h)
    raw_new = get_value("Last 24 Hours")
    new_snow = int(re.findall(r"\d+", raw_new)[0]) if raw_new else 0

    # 2️⃣ Base Depth (take first number)
    raw_depth = get_value("Base Depth")
    depth = int(re.findall(r"\d+", raw_depth)[0]) if raw_depth else 0

    # 3️⃣ Trails Open (80/82 → 80)
    raw_trails = get_value("Open Trails")
    num_trails = int(raw_trails.split("/")[0]) if raw_trails else 0

    # 4️⃣ Lifts Open (6/9 → 6)
    raw_lifts = get_value("Open Lifts")
    num_lifts = int(raw_lifts.split("/")[0]) if raw_lifts else 0

    # --- Final Output ---
    return {
        "JAY PEAK": {
            "trails": num_trails,
            "lifts": num_lifts,
            "depth": depth,
            "new snow": new_snow
        }
    }



# ft
def get_42_website():
    # --- URLs ---
    lifts_url = "https://api.killington.com/api/v1/dor/drupal/lifts"
    trails_url = "https://api.killington.com/api/v1/dor/drupal/trails"
    snow_url = "https://api.killington.com/api/v1/dor/drupal/snow-reports?sort=date&direction=desc"

    # --- Fetch Data ---
    lifts = requests.get(lifts_url).json()
    trails = requests.get(trails_url).json()
    snow_reports = requests.get(snow_url).json()

    # --- OPEN LIFTS ---
    open_lifts = sum(1 for lift in lifts if lift.get("status") == "open")

    # --- OPEN TRAILS ---
    # Count winter alpine trails only
    open_trails = 0
    for t in trails:
        if (
            t.get("season") == "winter"
            and t.get("type") == "alpine_trail"
            and t.get("include") is True
        ):
            if t.get("status") == "open":
                open_trails += 1

    # --- SNOW REPORT (newest entry) ---
    latest = snow_reports[0]

    base_depth = latest.get("base_depth", 0)
    new_snow_24h = latest.get("computed", {}).get("24_hour", 0)

    # --- RESULT ---
    return {
        "KILLINGTON": {
            "trails": open_trails,
            "lifts": open_lifts,
            "depth": base_depth,
            "new snow": new_snow_24h
        }
    }


def get_43_website():
    "last updated on 13 Jan 2024"
    """MAD RIVER GLEN:  https://www.madriverglen.com/conditions/"""
    
    url = "https://www.madriverglen.com/conditions/"
    r = requests.get(url)
    soup = bs(r.text , "lxml")
    
    all_lists = [d.text.strip() for d in soup.select("div.condition_pagetop_middle.fix > div.condition_middle_item.fix")]
    num_lifts = int([l for l in all_lists if "LIFTS" in l][0].replace("LIFTS" , ""))
    num_trails = int([l for l in all_lists if "TRAILS" in l][0].replace("TRAILS" , ""))
    new_snow = int([l for l in all_lists if "NEW SNOW" in l][0].replace("NEW SNOW" , "").split("-")[0])
    
    data_dict = {"MAD RIVER GLEN" : {"trails" : num_trails , 
                                    "lifts" : num_lifts , 
                                    "new snow" : new_snow}}
    
    return data_dict 

def get_44_website():

    url = "https://magicmtn.com/snow-report/"
    r = requests.get(url)
    soup = bs(r.text, "lxml")

    section = soup.select_one("section#comp-m8zyl320")
    if not section:
        return {"MAGIC MOUNTAIN": {}}

    # All h5 text elements inside the section
    h5s = section.select("h5")

    def find_value(label):
        """Return the numeric value BEFORE the h5 label."""
        for i, h in enumerate(h5s):
            if h.text.strip().upper() == label:
                # Look backward for a preceding <h5><span>VALUE</span></h5>
                if i == 0:
                    return 0
                prev = h5s[i - 1]
                val = prev.get_text(strip=True)
                nums = re.findall(r"\d+", val)
                return int(nums[0]) if nums else 0
        return 0

    # Extract key fields
    new_snow = find_value("24 HRS")

    # LIFTS is special because value is like "0/5"
    def find_lifts():
        for i, h in enumerate(h5s):
            if h.text.strip().upper() == "LIFTS":
                prev = h5s[i - 1].get_text(strip=True)
                nums = re.findall(r"\d+", prev)
                return int(nums[0]) if nums else 0
        return 0

    lifts = find_lifts()

    # TRAILS
    trails = find_value("TRAILS")

    return {
        "MAGIC MOUNTAIN": {
            "trails": trails,
            "lifts": lifts,
            "new snow": new_snow
        }
    }


# ft
def get_45_website():

    url = "https://ski-middlebury.app.alpinemedia.com/embed/lifts-trails/conditions?resort=middlebury-snowbowl"
    driver = headless_browser()
    driver.get(url)
    time.sleep(10)
    soup2 = bs(driver.page_source , "lxml")

  # matches "6 of 8 trails open", "0 of 12 trails open", etc.
    TRAIL_REGEX = re.compile(r"(\d+)\s+of\s+(\d+)\s+trails?\s+open", re.I)

    trail_blocks = TRAIL_REGEX.findall(soup2.get_text(" ", strip=True))

    total_open_trails = 0
    total_possible_trails = 0

    for open_t, total_t in trail_blocks:
        total_open_trails += int(open_t)
        total_possible_trails += int(total_t)

    # ----------------------------------
    # EXTRACT LIFT BLOCKS (similar format)
    # ----------------------------------

    LIFT_REGEX = re.compile(r"(\d+)\s+of\s+(\d+)\s+lifts?\s+open", re.I)

    lift_blocks = LIFT_REGEX.findall(soup2.get_text(" ", strip=True))

    total_open_lifts = 0
    total_possible_lifts = 0

    for open_l, total_l in lift_blocks:
        total_open_lifts += int(open_l)
        total_possible_lifts += int(total_l)

    return {
        "MIDDLEBURY SNOW BOWL": {
            "trails": total_open_trails,
            "lifts": total_open_lifts,
        }
    }



# ft
def get_46_website():
    """MOUNT SNOW:  https://www.mountsnow.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx"""
    
    url = "https://www.mountsnow.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx"
    r = requests.get(url)
    soup = bs(r.text , "lxml")
        
    num_lifts = int(soup.select("div[data-terrain-status-id='lifts']")[0].select("div.terrain_summary__circle")[0].get("data-open"))
    num_trails = int(soup.select("div[data-terrain-status-id='runs']")[0].select("div.terrain_summary__circle")[0].get("data-open"))
    
    url2 = "https://www.mountsnow.com/api/PageApi/GetWeatherDataForHeader"
    r2 = requests.get(url2)
    soup2 = bs(r2.text , "lxml")
    
    j = json.loads(r2.text)
    new_snow = int(j["SnowReportSections"][0]['Depth']['Inches'])
    depth = int(j["SnowReportSections"][-1]['Depth']['Inches'])
    
    data_dict = {"MOUNT SNOW" : {"trails" : num_trails,
                              "lifts" : num_lifts,
                              "depth" : depth,
                              "new snow" : new_snow}}
    
    return data_dict


# In[51]:
def get_47_website():
    """OKEMO:  https://www.okemo.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx"""
    
    url = "https://www.okemo.com/the-mountain/mountain-conditions/lift-and-terrain-status.aspx"
    r = requests.get(url)
    soup = bs(r.text , "lxml")
        
    num_lifts = int(soup.select("div[data-terrain-status-id='lifts']")[0].select("div.terrain_summary__circle")[0].get("data-open"))
    num_trails = int(soup.select("div[data-terrain-status-id='runs']")[0].select("div.terrain_summary__circle")[0].get("data-open"))
    
    url2 = "https://www.okemo.com/api/PageApi/GetWeatherDataForHeader"
    r2 = requests.get(url2)
    soup2 = bs(r2.text , "lxml")
    
    j = json.loads(r2.text)
    try:
        new_snow = int(j["SnowReportSections"][0]['Depth']['Inches'])
    except:
        new_snow = 0
        
    try:
        depth = int(j["SnowReportSections"][-1]['Depth']['Inches'])
    except:
        depth = 0
    data_dict = {"OKEMO" : {"trails" : num_trails,
                              "lifts" : num_lifts,
                              "depth" : depth,
                              "new snow" : new_snow}}
   
    
    return data_dict


# ft
def get_48_website():
    """SMUGGLERS NOTCH: https://www.smuggs.com/conditions/winter-report/"""
    
    url = "https://www.smuggs.com/conditions/winter-report/"
    r = requests.get(url)
    soup = bs(r.text, "lxml")
    
    # Extract Trails Open
    try:
        trails_section = soup.find("p", string="Trails Open").find_previous_sibling("div").find("span", class_="report-totals_subset")
        num_trails = int(trails_section.text.strip())
    except Exception:
        num_trails = 0

    # Extract Lifts Open
    try:
        lifts_section = soup.find("p", string="Lifts Open").find_previous_sibling("div").find("span", class_="report-totals_subset")
        num_lifts = int(lifts_section.text.strip())
    except Exception:
        num_lifts = 0

    # Extract New Snow
    try:
        new_snow_section = soup.find("p", string="New Snowfall").find_previous_sibling("div").find("span", class_="report-snow-data_amount")
        new_snow = int(new_snow_section.text.replace("″", "").strip())
    except Exception:
        new_snow = 0

    # Extract Man-Made Snow Depth
    try:
        man_made_snow_section = soup.find("p", string="Man-Made Snow Depth: 20 to 40″")
        man_made_snow_depth = int(man_made_snow_section.text.split(":")[1].split()[0])
    except Exception:
        man_made_snow_depth = 0

    data_dict = {
        "SMUGGLERS NOTCH": {
            "trails": num_trails,
            "lifts": num_lifts,
            "new snow": new_snow,
            "man-made snow depth": man_made_snow_depth,
        }
    }
    
    return data_dict

# In[53]:

# ft
def get_50_website():
    
    """STRATTON:  https://www.stratton.com/the-mountain/mountain-report"""
    params = {
        'format': 'json',
        'resortId': '1',
    }
    
    response = requests.get('https://www.mtnpowder.com/feed', params=params)
    soup = bs(response.text , "lxml")
    
    j = json.loads(response.text)
    
    num_lifts = j['SnowReport']['TotalOpenLifts']
    num_trails = j['SnowReport']['TotalOpenTrails']
    depth = float(j['SnowReport']["BaseArea"]['BaseIn'])
    
    data_dict = {"STRATTON" : {"trails" : num_trails,
                              "lifts" : num_lifts,
                              "depth" : depth}}
    
    return data_dict

# ft
def get_51_website():
    
    """SUGARBUSH:  https://www.sugarbush.com/mountain/conditions"""
    
    
    url = 'https://www.mtnpowder.com/feed?format=json&resortId=70'
    r = requests.get(url)
    j = json.loads(r.text)
        
    num_lifts = j['SnowReport']['TotalOpenLifts']
    num_trails = j['SnowReport']['TotalOpenTrails']
    new_snow = float(j['SnowReport']["BaseArea"]['Last24HoursIn'])
    depth = float(j['SnowReport']["BaseArea"]['BaseIn'])
    
    data_dict = {"SUGARBUSH" : {"trails" : num_trails,
                              "lifts" : num_lifts,
                              "depth" : depth,
                              "new snow" : new_snow}}
    return data_dict

# ft
def get_52_website():
    """LOON https://www.loonmtn.com/mountain-report"""

    url = "https://www.loonmtn.com/mountain-report"

    driver = headless_browser()

    try:
        driver.get(url)
        time.sleep(5)

        lifts_num = 0
        trails_num = 0
        new_snow = 0 

        elements = driver.find_elements(By.CSS_SELECTOR, "div.relative.flex.h-44.w-44")
        lifts_num = int(elements[0].find_element(By.CSS_SELECTOR, "span.h2").text.strip())
        trails_num = int(elements[1].find_element(By.CSS_SELECTOR, "span.h2").text.strip())

        data_dict = {
            "LOON": {
                "lifts": lifts_num,
                "trails": trails_num,
                "new snow": new_snow
            }
        }
        
        return data_dict
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()

def get_53_website():

    url = "https://skiburke.com/the-mountain/weather-conditions#lifts"
    r = requests.get(url)
    soup = bs(r.text, "lxml")

    # ---------------------------------------------
    # 1️⃣ SNOWFALL — extract 24 hours
    # ---------------------------------------------
    snowfall_rows = soup.select("table.uk-table tbody tr")

    snowfall_24h = ""
    for row in snowfall_rows:
        title = row.select_one("td .el-title")
        value = row.select_one("td .el-text_1")
        if title and value and "24 Hours" in title.text:
            snowfall_24h = value.text.strip().replace('"', "")
            break

    # ---------------------------------------------
    # 2️⃣ LIFT STATUS (open lifts)
    # ---------------------------------------------
    lift_rows = soup.select("table.uk-table-divider tbody tr")

    open_lifts = 0
    closed_lifts = 0

    for tr in lift_rows:
        td_open = tr.select_one("td:nth-child(2) span.uk-text-success")
        td_closed = tr.select_one("td:nth-child(3) span.uk-text-danger")

        if td_open:
            open_lifts += 1
        elif td_closed:
            closed_lifts += 1

    # ---------------------------------------------
    # 3️⃣ TRAIL STATUS (open trails)
    #     Two separate tables → count both
    # ---------------------------------------------
    trail_rows = soup.select("table.uk-table.uk-table-divider tbody.fs-load-more-container tr")

    open_trails = 0

    for tr in trail_rows:
        # Green = open → span.uk-text-success
        is_open = tr.select_one("td:nth-child(3) span.uk-text-success")
        if is_open:
            open_trails += 1

    # ---------------------------------------------
    # 4️⃣ Final Output
    # ---------------------------------------------
    return {
        "BURKE": {
            "snow_24h": snowfall_24h,
            "lifts": open_lifts,
            "trails": open_trails
        }
    }

def get_54_website():
    """BIG MOOSE MOUNTAIN: Extract data using Selenium"""
    
    # URL to scrape
    url = "https://skibigmoose.com/trail-report-1"
    
    driver = headless_browser()
    
    try:
        # Open the website
        driver.get(url)
        
        # Wait for the page to load (adjust time if necessary)
        driver.implicitly_wait(10)
        
        # Locate the lifts section based on its attributes
        lifts_element = driver.find_element(By.CSS_SELECTOR, "h4[data-aid='MENU_SECTION1_ITEM0_TITLE']")
        num_lifts = int(lifts_element.text.strip()) if lifts_element else 0

        # Placeholder for other values
        num_trails = 0
        depth = 0.0
        new_snow = 0.0

        # Prepare the data dictionary
        data_dict = {
            "BIG MOOSE MOUNTAIN": {
                "trails": num_trails,
                "lifts": num_lifts,
                "depth": depth,
                "new snow": new_snow
            }
        }
        return data_dict
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "BIG MOOSE MOUNTAIN": {
                "trails": 0,
                "lifts": 0,
                "depth": 0.0,
                "new snow": 0.0
            }
        }
    
    finally:
        # Close the WebDriver
        driver.quit()

def get_55_website():
    """BLUE HILLS: https://bluehillsboston.com/"""
    
    driver = headless_browser()
    
    try:
        # Navigate to the URL
        url = "https://bluehillsboston.com/"
        driver.get(url)
        time.sleep(5)

        # Scroll until Trails element is in view
        trails_element = driver.find_element(By.CLASS_NAME, "kb-count-up-675_bf195d-06")
        ActionChains(driver).move_to_element(trails_element).perform()
        driver.execute_script("window.scrollBy(0, 100);")
        time.sleep(2)  # Allow time for the element to fully load
        num_trails = int(trails_element.find_element(By.CLASS_NAME, "kb-count-up-number").text.strip())

        # Scroll until Lifts element is in view
        lifts_element = driver.find_element(By.CLASS_NAME, "kb-count-up-675_08f35b-86")
        ActionChains(driver).move_to_element(lifts_element).perform()
        time.sleep(2)  # Allow time for the element to fully load
        num_lifts = int(lifts_element.find_element(By.CLASS_NAME, "kb-count-up-number").text.strip())

    except Exception as e:
        # print(f"An error occurred: {e}")
        num_trails, num_lifts = 0, 0
    
    finally:
        # Close the WebDriver
        driver.quit()
    
    # Placeholder for depth and new snow
    depth = 0.0
    new_snow = 0.0

    # Prepare the data dictionary
    data_dict = {
        "BLUE HILLS": {
            "trails": num_trails,
            "lifts": num_lifts,
            "depth": depth,
            "new snow": new_snow
        }
    }
    return data_dict

def get_56_website():
    """SKI BRADFORD:  https://skibradford.com/snow-report/"""
    
    url = "https://skibradford.com/snow-report/"
    driver = headless_browser()
    driver.get(url)
    time.sleep(5)
    soup = bs(driver.page_source, "lxml")
    
    try:
        # Extract Trails count
        trails_element = soup.find("p", string=lambda text: "Total Trails Open" in text).text
        num_trails = int(trails_element.split()[-1])  # Get the last number in the string
        
        # Extract Lifts count
        lifts_element = soup.find("p", string=lambda text: "Total Lifts Open" in text).text
        num_lifts = int(lifts_element.split()[-1])  # Get the last number in the string

    except Exception as e:
        print(f"An error occurred: {e}")
        num_trails, num_lifts = 0, 0
    
    # Placeholder for depth and new snow
    depth = 0.0
    new_snow = 0.0

    # Prepare the data dictionary
    data_dict = {
        "SKI BRADFORD": {
            "trails": num_trails,
            "lifts": num_lifts,
            "depth": depth,
            "new snow": new_snow
        }
    }
    
    return data_dict

def get_57_website():
    """GUNSTOCK:  https://www.gunstock.com/winter/snow-report/"""
    
    driver = headless_browser()
    
    try:
        # Navigate to the URL
        url = "https://www.gunstock.com/winter/snow-report/"
        driver.get(url)
        time.sleep(12)  # Allow some time for the page to fully load
        
        # Find all "dl" elements with the specific class
        dl_elements = driver.find_elements(By.CSS_SELECTOR, "dl.SnowReport-measure.trails-lifts")
        # print(len(dl_elements))
        # Initialize variables
        num_lifts, num_trails = 0, 0
        
        # Extract values for Lifts and Trails
        if len(dl_elements) >= 2:  # Ensure two `dl` elements exist
            lifts_dd = dl_elements[0].find_element(By.TAG_NAME, "dd")
            lifts_span = lifts_dd.find_elements(By.TAG_NAME, "span")
            # print("Lifts Span HTML:", lifts_span[0].get_attribute("outerHTML"))  # Debug

            num_lifts = int(lifts_span[0].get_attribute("textContent").strip() or "0")
            # print("Lifts Value:", num_lifts)

            # Extract Trails
            trails_dd = dl_elements[1].find_element(By.TAG_NAME, "dd")
            trails_span = trails_dd.find_elements(By.TAG_NAME, "span")
            # print("Trails Span HTML:", trails_span[0].get_attribute("outerHTML"))  # Debug

            num_trails = int(trails_span[0].get_attribute("textContent").strip() or "0")
            # print("Trails Value:", num_trails) 
            # Locate the base depth container using CSS selector
            base_depth_container = driver.find_elements(
                By.CSS_SELECTOR, "div.SnowReport-measures.SnowReport-measures--columns.d-flex.justify-content-between.justify-content-evenly"
            )

            # print(len(base_depth_container))
            base_depth_dd = base_depth_container[1].find_element(By.TAG_NAME, "dd")
            base_depth_text = base_depth_dd.get_attribute("textContent").strip()
            base_depth = int(re.findall(r"\d+", base_depth_text)[0])  # Extract the first number (6)

    except Exception as e:
        print(f"An error occurred: {e}")
        num_trails, num_lifts, base_depth = 0, 0, 0.0
        
    except Exception as e:
        print(f"An error occurred: {e}")
        num_trails, num_lifts = 0, 0
    
    finally:
        # Close the browser
        driver.quit()
    
    # Placeholder for depth and new snow
    new_snow = 0.0

    # Prepare the data dictionary
    data_dict = {
        "GUNSTOCK": {
            "trails": num_trails,
            "lifts": num_lifts,
            "depth": base_depth,
            "new snow": new_snow
        }
    }
    
    return data_dict

def get_58_website():
    """MCINTYRE: https://www.mcintyreskiarea.com/mountain-report/"""

    driver = headless_browser()

    try:
        # Load the page
        url = "https://www.mcintyreskiarea.com/mountain-report/"
        driver.get(url)

        # Find all 'p' elements with the class 'pp-info-table-subtitle'
        trails_lifts_elements = driver.find_elements(By.CLASS_NAME, "pp-info-table-subtitle")
        
        # Count <br> tags for Lifts (1st element) and Trails (2nd element)
        num_lifts = 1 + len(trails_lifts_elements[0].find_elements(By.TAG_NAME, "br"))
        num_trails = 1 + len(trails_lifts_elements[1].find_elements(By.TAG_NAME, "br"))

    except Exception as e:
        print(f"Error occurred: {e}")
        num_trails, num_lifts = 0, 0

    finally:
        # Quit the driver
        driver.quit()

    # Prepare the result
    data_dict = {
        "MCINTYRE": {
            "trails": num_trails,
            "lifts": num_lifts
        }
    }
    return data_dict

def get_59_website():
    """TENNEY MOUNTAIN: https://skitenney.com/report/"""

    url = "https://skitenney.propapps.io/snow-report/"

    browser = headless_browser()

    browser.get(url)
    time.sleep(10)

    # Parse HTML inside iframe
    html = browser.page_source
    soup = bs(html, "lxml")

    # --------------------------------------------------
    # Extract LIFTS OPEN
    # <h2>Lifts Open</h2> → next <dd> contains "1 of 4"
    # --------------------------------------------------
    try:
        lifts_h2 = soup.find("h2", string=lambda x: x and "Lifts Open" in x)
        dd = lifts_h2.find_next("dd")
        nums = re.findall(r"\d+", dd.text)
        lifts_open = int(nums[0])
    except:
        lifts_open = 0

    # --------------------------------------------------
    # Extract TRAILS OPEN
    # <h2>Trails Open</h2> → next <dd> contains "10 of 53"
    # --------------------------------------------------
    try:
        trails_h2 = soup.find("h2", string=lambda x: x and "Trails Open" in x)
        dd = trails_h2.find_next("dd")
        nums = re.findall(r"\d+", dd.text)
        trails_open = int(nums[0])
    except:
        trails_open = 0

    # --------------------------------------------------
    # Extract NEW SNOW (Past 24 Hours)
    # <dt>Past 24 Hours</dt> → next <dd> contains snow amount
    # --------------------------------------------------
    try:
        row = soup.find("dt", string=lambda x: x and "Past 24 Hours" in x)
        dd = row.find_next("dd")
        nums = re.findall(r"\d+", dd.text)
        new_snow = int(nums[0]) if nums else 0
    except:
        new_snow = 0

    browser.quit()

    return {
        "TENNEY MOUNTAIN": {
            "trails": trails_open,
            "lifts": lifts_open,
            "new snow": new_snow
        }
    }


def get_60_website():
    """PICO: https://www.picomountain.com/the-mountain/conditions-weather/current-conditions-weather"""

    driver = headless_browser()

    try:
        # Load the page
        url = "https://www.picomountain.com/the-mountain/conditions-weather/current-conditions-weather"
        driver.get(url)
        time.sleep(5)  # Wait for content to load

        # Find all measurement items
        measurement_items = driver.find_elements(By.CSS_SELECTOR, "div.styles__StyledDorMeasurementItem-sc-efp7vw-0")

        # Initialize variables
        num_trails = 0
        num_lifts = 0

        # Loop through the measurement items and find the correct labels
        num_lifts = measurement_items[2].find_element(By.CLASS_NAME, "percent-primary-text").text.strip()
        num_trails = measurement_items[3].find_element(By.CLASS_NAME, "percent-primary-text").text.strip()

        # Extract Base Depth and New Snow (48 Hour) from the <ul>
        base_depth, new_snow = 0, 0
        report_items = driver.find_elements(By.CSS_SELECTOR, "ul.styles__ReportDataItems-sc-1kqptpn-8 li")
        for item in report_items:
            header = item.find_element(By.CLASS_NAME, "styles__ItemHeader-sc-1kqptpn-10").text.strip()
            value = item.find_element(By.CLASS_NAME, "styles__ItemValue-sc-1kqptpn-12").text.strip()

            if header == "Base-Depth":
                base_depth = int(value.replace('"', "").strip())  # Remove double quotes
            elif header == "48 Hour":
                new_snow = int(value.replace('"', "").strip())  # Remove double quotes

    except Exception as e:
        print(f"Error occurred: {e}")
        num_trails, num_lifts, base_depth, new_snow = 0, 0, 0, 0

    finally:
        # Quit the driver
        driver.quit()

    # Prepare the result
    data_dict = {
        "PICO": {
            "trails": num_trails,
            "lifts": num_lifts,
            "base depth": base_depth,
            "new snow": new_snow
        }
    }
    return data_dict

def get_61_website():
    """SASKADENA SIX: Extract number of open lifts and trails."""
    import requests
    from bs4 import BeautifulSoup

    url = "https://www.saskadenasix.com/the-mountain/conditions"
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "lxml")

    # -----------------------------
    # FIND LIFTS & TRAILS SECTIONS
    # -----------------------------
    lifts_open = 0
    trails_open = 0

    # Find the entire content container
    container = soup.select_one("div.listing-row.lifts-trails")
    if not container:
        return {"SASKADENA SIX": {"lifts": 0, "trails": 0}}

    elements = container.find_all(["h2", "article"])

    section = None  # "lifts" or "trails"

    for el in elements:

        # Detect section start
        if el.name == "h2":
            text = el.get_text(strip=True).lower()
            if "lifts" in text:
                section = "lifts"
            elif "trails" in text:
                section = "trails"
            continue

        # Skip if not inside a section
        if el.name != "article" or not section:
            continue

        # Read status field
        status_div = el.select_one("div.cell.status")
        status_text = status_div.get_text(strip=True).lower() if status_div else ""

        is_open = ("open" in status_text) and ("closed" not in status_text)

        if section == "lifts":
            if is_open:
                lifts_open += 1

        if section == "trails":
            if is_open:
                trails_open += 1

    return {
        "SASKADENA SIX": {
            "lifts": lifts_open,
            "trails": trails_open,
        }
    }



def get_final_json_data():
    """this function combines all the extracted data from all 50 websites into one json file with the name of data_today_date.json"""
    final_json = []

    global empty_data_dict




# # -----------------------------------
#     try:
#         data = get_1_website()
#         print('1 website is done scraping' )
#     except:
#         data = { 'MOHAWK MOUNTAIN' : empty_data_dict }
#         None
#     final_json.append(data)
# #-----------------------------------
#     try:
#         data = get_2_website()
#         print('2 website is done scraping' )
#     except:
#         data = { 'MOUNT SOUTHINGTON' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     # try:
#     #     data = get_3_website()
#     #     print('3 website is done scraping' )
#     # except:
#     #     data = { 'POWDER RIDGE' : empty_data_dict }
#     #     None
#     # final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_4_website()
#         print('4 website is done scraping' )
#     except:
#         data = { 'SKI SUNDOWN' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     # try:
#     #     data = get_5_website()
#     #     print('5 website is done scraping' )
#     # except:
#     #     data = { 'BIGROCK' : empty_data_dict }
#     #     None
#     # final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_6_website()
#         print('6 website is done scraping' )
#     except:
#         data = { 'BLACK MOUNTAIN ME' : empty_data_dict }
#         None
#     final_json.append(data)
# #-----------------------------------
#     try:
#         data = get_7_website()
#         print('7 website is done scraping' )
#     except:
#         data = { 'CAMDEN SNOW BOWL' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_8_website()
#         print('8 website is done scraping' )
#     except:
#         data = { 'LOST VALLEY' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_9_website()
#         print('9 website is done scraping' )
#     except:
#         data = { 'MOUNT ABRAM' : empty_data_dict }
#         None
#     final_json.append(data)
# # # -----------------------------------
#     try:
#         data = get_10_website()
#         print('10 website is done scraping' )
#     except:
#         data = { 'SADDLEBACK' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_11_website()
#         print('11 website is done scraping' )
#     except:
#         data = { 'PLEASANT MOUNTAIN' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_12_website()
#         print('12 website is done scraping' )
#     except:
#         data = { 'SUGARLOAF' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_13_website()
#         print('13 website is done scraping' )
#     except:
#         data = { 'SUNDAY RIVER' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_14_website()
#         print('14 website is done scraping' )
#     except:
#         data = { 'BERKSHIRE EAST' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_15_website()
#         print('15 website is done scraping' )
#     except:
#         data = { 'BOUSQUET' : empty_data_dict }
#         None
#     final_json.append(data)
# #-----------------------------------
#     try:
#         data = get_16_website()
#         print('16 website is done scraping' )
#     except:
#         data = { 'CATAMOUNT' : empty_data_dict }
#         None
#     final_json.append(data)
# #-----------------------------------
#     try:
#         data = get_17_website()
#         print('17 website is done scraping' )
#     except:
#         data = { 'JIMINY PEAK' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_18_website()
#         print('18 website is done scraping' )
#     except:
#         data = { 'NASHOBA VALLEY' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_19_website()
#         print('19 website is done scraping' )
#     except:
#         data = { 'BRADFORD' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_20_website()
#         print('20 website is done scraping' )
#     except:
#         data = { 'BUTTERNUT' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_21_website()
#         print('21 website is done scraping' )
#     except:
#         data = { 'SKI WARD' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_22_website()
#         print('22 website is done scraping' )
#     except:
#         data = { 'WACHUSETT' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_23_website()
#         print('23 website is done scraping' )
#     except:
#         data = { 'ATTITASH' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_24_website()
#         print('24 website is done scraping' )
#     except:
#         data = { 'BRETTON WOODS' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_25_website()
#         print('25 website is done scraping' )
#     except:
#         data = { 'BLACK MOUNTAIN NH' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_26_website()
#         print('26 website is done scraping' )
#     except:
#         data = { 'CANNON MOUNTAIN' : empty_data_dict }
#         None
#     final_json.append(data)
# #-----------------------------------
#     try:
#         data = get_27_website()
#         print('27 website is done scraping' )
#     except:
#         data = { 'CRANMORE' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_28_website()
#         print('28 website is done scraping' )
#     except:
#         data = { 'CROTCHED' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
    
#     try:
#         data = get_29_website()
#         print('29 website is done scraping' )
#     except:
#         data = { 'DARTMOUTH SKIWAY' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_30_website()
#         print('30 website is done scraping' )
#     except:
#         data = { 'KING PINE' : empty_data_dict }
#         None
#     final_json.append(data)

# # #-----------------------------------

#     try:
#         data = get_31_website()
#         print('31 website is done scraping' )
#     except:
#         data = { 'MOUNT SUNAPEE' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_32_website()
#         print('32 website is done scraping' )
#     except:
#         data = { 'PATS PEAK' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_33_website()
#         print('33 website is done scraping' )
#     except:
#         data = { 'RAGGED MOUNTAIN' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_34_website()
#         print('34 website is done scraping' )
#     except:
#         data = { 'WATERVILLE VALLEY' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_35_website()
#         print('35 website is done scraping' )
#     except:
#         data = { 'WHALEBACK' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_36_website()
#         print('36 website is done scraping' )
#     except:
#         data = { 'WILDCAT' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_37_website()
#         print('37 website is done scraping' )
#     except:
#         data = { 'YAWGOO VALLEY' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_38_website()
#         print('38 website is done scraping' )
#     except:
#         data = { 'BOLTON VALLEY' : empty_data_dict }
#         None
#     final_json.append(data)
# #-----------------------------------
#     try:
#         data = get_39_website()
#         print('39 website is done scraping' )
#     except:
#         data = { 'BROMLEY' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_40_website()
#         print('40 website is done scraping' )
#     except:
#         data = { 'BURKE' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_41_website()
#         print('41 website is done scraping' )
#     except:
#         data = { 'JAY PEAK' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_42_website()
#         print('42 website is done scraping' )
#     except:
#         data = { 'KILLINGTON' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_43_website()
#         print('43 website is done scraping' )
#     except:
#         data = { 'MAD RIVER GLEN' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_44_website()
#         print('44 website is done scraping' )
#     except:
#         data = { 'MAGIC MOUNTAIN' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_45_website()
#         print('45 website is done scraping' )
#     except:
#         data = { 'MIDDLEBURY SNOW BOWL' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_46_website()
#         print('46 website is done scraping' )
#     except:
#         data = { 'MOUNT SNOW' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_47_website()
#         print('47 website is done scraping' )
#     except:
#         data = { 'OKEMO' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_48_website()
#         print('48 website is done scraping' )
#     except:
#         data = { 'SMUGGLERS NOTCH' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     # try:
#     #     data = get_49_website()
#     #     print('49 website is done scraping' )
#     # except:
#     #     data = { 'STOWE' : empty_data_dict }
#     #     None
#     # final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_50_website()
#         print('50 website is done scraping' )
#     except:
#         data = { 'STRATTON' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_51_website()
#         print('51 website is done scraping' )
#     except:
#         data = { 'SUGARBUSH' : empty_data_dict }
#         None
#     final_json.append(data)
# # # -----------------------------------
#     try:
#         data = get_52_website()
#         print('52 website is done scraping' )
#     except:
#         data = { 'LOON' : empty_data_dict }
#         None
#     final_json.append(data)
# -----------------------------------
#     try:
#         data = get_53_website()
#         print('53 website is done scraping' )
#     except:
#         data = { 'BURKE' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_54_website()
#         print('54 website is done scraping' )
#     except:
#         data = { 'BIG MOOSE MOUNTAIN' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_55_website()
#         print('55 website is done scraping' )
#     except:
#         data = { 'BIG MOOSE MOUNTAIN' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_56_website()
#         print('56 website is done scraping' )
#     except:
#         data = { 'SKI BRADFORD' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_57_website()
#         print('57 website is done scraping' )
#     except:
#         data = { 'GUNSTOCK' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_58_website()
#         print('58 website is done scraping' )
#     except:
#         data = { 'MCINTYRE' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_59_website()
#         print('59 website is done scraping' )
#     except:
#         data = { 'TENNEY MOUNTAIN' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
#     try:
#         data = get_60_website()
#         print('60 website is done scraping' )
#     except:
#         data = { 'PICO' : empty_data_dict }
#         None
#     final_json.append(data)
# # #-----------------------------------
    try:
        data = get_61_website()
        print('61 website is done scraping' )
    except:
        data = { 'SASKADENA SIX' : empty_data_dict }
        None
    final_json.append(data)
#-----------------------------------
    # if new_source == True:
    #     print('52 website is done scraping' )
        
    return final_json
    

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
 


# In[67]:


def write_final_json_file():
    """this function scrape all the data from all sources and write them into a json file"""
    print("getting the data from all the sources")
    global t1
    

    json_data = get_final_json_data()
    
    # today = datetime.datetime.now().strftime("%Y_%m_%d")
    # today_hourly = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    
    try:
        os.remove(f"data.json")
        
    except:
        None
    print('===========================')
    # os.chdir("C:\\Users\\A.J\\Documents\\GitHub\\skiconditions") 
    os.chdir("C:") 
    print(f"the directory of the  data.json file is {os.getcwd()}")
    
    with open(f"data.json" , "w") as file:
        file.write(json.dumps(json_data , cls=NpEncoder))

      
    print(f"your data is stored in data.json ")
    print("the scraping for today is finished")
    t2 = time.time()

    print(f"the overall time for scraping is {(t2 - t1)/60} minutes only")
    print(f" 51 websites are scraped into .json file with name of data.json")
#     return json_data

# In[ ]:

# write_final_json_file()
# scheduling the code to run every day at 6 am

#schedule.every().day.at("06:00").do(write_final_json_file)
#schedule.every().day.at("12:00").do(write_final_json_file)
# schedule.every(1).hour.do(write_final_json_file)
# schedule.every(3).minutes.do(write_final_json_file)
write_final_json_file()
# time.sleep(20)
