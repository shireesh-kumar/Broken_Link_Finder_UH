import requests
import csv
from bs4 import BeautifulSoup
import urllib3
import json
from datetime import datetime
from tqdm import tqdm
import sys
from playwright.sync_api import sync_playwright


def test_links_with_playwright(links_to_test, broken_links, page):
    for link_data in links_to_test:
        try:
            response = page.goto(link_data['url'], timeout=15000, wait_until="load")
            if response.status >= 300:
                broken_links.append({link_data['text']: link_data['url'], "status_code": response.status})
        except Exception:
            broken_links.append({link_data['text']: link_data['url'], "status_code": "playwright_error"})
            
def crawl(session_req):
    broken_report = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        with open('UH_Links.csv', mode='r') as file:
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
                    playwright_links = []
                    with tqdm(total=len(full_list_links), desc="Processing", disable=not sys.stdout.isatty()) as pbar: 
                        for i in full_list_links:
                            link = str(i.attrs.get('href'))
                            if link.startswith("http"):
                                res = requests.get(headers = headers,url=link,verify=False, timeout=(5, 15), allow_redirects=True)
                                if res.status_code >= 300:
                                    if "uh.edu" in link:
                                        broken_links.append({i.text:link, "status_code": res.status_code})
                                    else:
                                        playwright_links.append({'text': i.text, 'url': link})
                            pbar.update(1)
                    
                    test_links_with_playwright(playwright_links, broken_links, page)  
                    broken_report[eachline[0]] = broken_links
                except Exception as ex:
                    print(f"Error: {type(ex).__name__} - {ex}")
        
        browser.close()
  
    now = datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d-%H-%M-%S")

    with open(f'output/broken_report_{formatted_date_time}.json', 'w') as json_file:
        json.dump(broken_report, json_file, indent=4)
    
if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session_req = requests.Session()
    crawl(session_req)
        

