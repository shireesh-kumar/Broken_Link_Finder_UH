import requests
import csv
from bs4 import BeautifulSoup
import urllib3
import json
from datetime import datetime
from tqdm import tqdm
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def check_link(url,driver):
    try:
        driver.get(url)
        return True
    except Exception as e:
        return False

def crawl(session_req):
    broken_report = {}
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    with open('UH_Test_Links.csv', mode='r') as file:
        csvFile = csv.reader(file)
        headers = {"User-Agent": "PostmanRuntime/7.50.0"}

        for eachline in csvFile:
            try:
                broken_links = []
                response = session_req.get(url=eachline[0])
                if response.status_code != 200:
                    broken_report[eachline] = "Page link error in UH_Links CSV file"
                    continue

                html_data = BeautifulSoup(response.text, 'html.parser')
                
                body = html_data.find('body')
                if body:
                    main = body.find('main')
                    if main:
                        html_data = main
                    else:
                        raise Exception("Main tag not found in body")
                
                
                full_list_links = html_data.find_all('a')
                
                with tqdm(total=len(full_list_links), desc="Processing", disable=not sys.stdout.isatty()) as pbar: 
                    for i in full_list_links:
                        link = str(i.attrs.get('href'))
                        if link.startswith("http"):
                            res = requests.get(headers = headers,url=link,verify=False, timeout=(5, 15), allow_redirects=True)
                            if res.status_code >= 400:
                                if not check_link(link,driver):
                                    broken_links.append({i.text:link, "status_code": res.status_code})
                        pbar.update(1)  
                broken_report[eachline[0]] = broken_links
            except Exception as ex:
                print(f"Error: {type(ex).__name__} - {ex}")
  
    now = datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d-%H-%M-%S")

    with open(f'output/broken_report_{formatted_date_time}.json', 'w') as json_file:
        json.dump(broken_report, json_file, indent=4)
    
    driver.quit()        

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session_req = requests.Session()
    crawl(session_req)
        

