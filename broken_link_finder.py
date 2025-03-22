import requests
import csv
from bs4 import BeautifulSoup
import urllib3
import json
from datetime import datetime

def crawl(session_req):
    broken_report = {}
    with open('UH_Links.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for eachline in csvFile:
            try:
                broken_links = []
                response = session_req.get(url=eachline[0])
                if response.status_code != 200:
                    broken_report[eachline] = "Page link error in UH_Links CSV file"
                    continue

                html_data = BeautifulSoup(response.text, 'html.parser')
                
                for section in html_data.select('.uh-footer.uh-footer-brick, .uh-header.uh-header-secondary'):
                    section.decompose()
                
                full_list_links = html_data.find_all('a')
                for i in full_list_links:
                    link = str(i.attrs.get('href'))
                    if not link.startswith("http"):
                        continue
                    res = requests.get(url=link,verify=False)
                    if res.status_code != 200:
                        broken_links.append({i.text:link})
            
                broken_report[eachline[0]] = broken_links
            except requests.exceptions.RequestException as ex:
                print(ex)
        
    now = datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    with open(f'output/broken_report_{formatted_date_time}.json', 'w') as json_file:
        json.dump(broken_report, json_file, indent=4)
            

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session_req = requests.Session()
    crawl(session_req)
        

