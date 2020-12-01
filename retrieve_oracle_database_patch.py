from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
import fileinput
import os
import os.path
from datetime import datetime
from datetime import datetime
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request as urllib2 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome import options

#credentials to login to oracle
email = "<Enter Email Here>"
password = "<Enter Password Here>"
month = ""
year = ""
lookup_OS = "Linux x86-64"
lookuparu = 'aru'

##removing and creating of text files##
patch_table1 = "specific_patch_table.txt"
if os.path.exists(patch_table1):
    os.remove(patch_table1)
else:
    create_patch_table = open("specific_patch_table.txt","w")

patch_table5 = "html.txt"
if os.path.exists(patch_table5):
    os.remove(patch_table5)
else:
    create_patch_table = open("html.txt","w")
##removing and creating of text files##

current_dir = os.getcwd()
##enable headless download##
def enable_download_headless(browser,download_dir):
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--verbose')
chrome_options.add_experimental_option("prefs", {
        "download.default_directory": current_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
})

chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-software-rasterizer')

driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
download_dir = current_dir
enable_download_headless(driver, download_dir)
##enable headless download##

#retrieve url
driver.get('https://support.oracle.com/epmos/faces/Dashboard')

time.sleep(5)

#pass credentials into website
driver.find_element_by_id("sso_username").send_keys(email)
driver.find_element_by_id("ssopassword").send_keys(password)

time.sleep(5)

#submit credentials by clicking on button
submitbutton = driver.find_elements_by_xpath("/html/body/div/div[3]/div[1]/form/div[2]/span/input")
for btn in submitbutton:
    btn.click()


#get current month & year
now = datetime.now()
month = now.strftime("%m")
year = now.strftime("%Y")
if month == "01":
    month = "jan"
    driver.get(f'https://www.oracle.com/security-alerts/cpu{month}{year}.html')
elif month == "04":
    month = "apr"
    driver.get(f'https://www.oracle.com/security-alerts/cpu{month}{year}.html')
elif month == "07":
    month = "jul"
    driver.get(f'https://www.oracle.com/security-alerts/cpu{month}{year}.html')
elif month == "10":
    month = "oct"
    driver.get(f'https://www.oracle.com/security-alerts/cpu{month}{year}.html')
else:
    exit()


html = driver.page_source
soup = BeautifulSoup(html, features="html.parser")
for a in soup.find_all(href=True):
    if "Database" in a.contents:
        page_source = open("html.txt","w")
        page_source.write(a["href"])
        page_source.close()
f = open("html.txt")
database = f.readline()
f.close()

driver.get(f'{database}')

#get oracle database 12 updates table
latest_patch = driver.find_elements_by_xpath("//*[@id='kmPgTpl:r1:ot71']/div[1]/div/div[3]/div/table[11]")
for patch in latest_patch:
    patchnumbers = patch.text
    file = open("latest_patch.txt","w")
    time.sleep(3)
    #write the text from the oracle database 12 updates table into a file
    file.write(patchnumbers)
    file.close()
    f = open("latest_patch.txt","r")
    lines = f.readlines()
    for i in range(0, len(lines)):
        values = lines[i]
        pattern = r'(\d{8})'
        pattern1 = r'[G][I]\s[a-zA-Z]{7}'
        text = re.findall(pattern1,values)
        text1 = re.findall(pattern,values)
        #if string in file match "GI" && "{any 8 digits number} in the same line, it will take the 8 digit number"
        #E.g. Combo OJVM Release Update 12.2.0.1.200114 and GI Release Update 12.2.0.1.200114 Patch 30463673 -> var patch_no = 30463673
        if (text and text1):
            test = str(text1)
            patch_no = test.strip("[']")
            driver.get(f"https://support.oracle.com/epmos/faces/ui/patch/PatchDetail.jspx?parent=DOCUMENT&sourceId=2602410.1&patchId={patch_no}")
            time.sleep(5)
            #table of all the database in different OS
            patch_table = driver.find_elements_by_xpath("//*[@id='pt1:r1:0:gts1:gts_pc1:resTbl']")
            for u in patch_table:
                patches_text = u.text
                file = open("patch_table.txt","w+")
                file.write(patches_text)
                file.close()
                f1 = open("patch_table.txt","r")
                patchlines = f1.readlines()
                lookup_patch = patch_no
                matchedline = ''
                for t in patchlines:
                    if lookup_patch in t:
                        matchedline = t
                        #remove unnecessary lines in textfile and extract lines with the patch_no
                        with open("specific_patch_table.txt", "a+") as f2:
                            f2.write(matchedline)
                            f2.close()
                            f3 = open("specific_patch_table.txt","r")
                            for num, line in enumerate(f3, 0):
                                if lookup_OS in line:
                                    # within the text file - get row number of where the linux patch is on
                                    line_no = str(num)
                                    patch_link = driver.find_elements_by_xpath(f"//*[@id='pt1:r1:0:gts1:gts_pc1:resTbl:{line_no}:cl1']")
                                    for patch_btn in patch_link:
                                        patch_btn.click()
                                        time.sleep(3)
                                        #get website's page source and extract all links (href)
                                        html = driver.page_source
                                        soup = BeautifulSoup(html, features="html.parser")
                                        for a in soup.find_all(href=True):
                                            page_source = open("html.txt","a")
                                            page_source.write(str(a))
                                            page_source.close()
                                        page_text = open("html.txt", "r")
                                        patchlines = page_text.readlines()
                                        for i in range(0, len(patchlines)):
                                            values = patchlines[i]
                                            pattern = r'[a][r][u]=[^;]*\d{8}'
                                            # if text in file contains "aru", extract the 8 digits afterwards
                                            aru_text = re.findall(pattern,values)
                                            if (text):
                                                aru = str(aru_text)
                                                aru_no = aru.strip("[aru=']")
                                                if os.path.isfile(f"{current_dir}/p{patch_no}_122010_Linux-x86-64.zip"):
                                                    exit()
                                                else:
                                                    driver.get(f"https://updates.oracle.com/Orion/Services/download/p{patch_no}_122010_Linux-x86-64.zip?aru={aru_no}&patch_file=p{patch_no}_122010_Linux-x86-64.zip")
