import json
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import os, sys

URL = "https://freedns.afraid.org/domain/registry/page-"
OUTPUT_FILE = "fdns-output.json"

session = requests.Session()

# header stuff token STRAIGHT from the good freedns domain scraper
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://freedns.afraid.org/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
})

def get_domain_id(href):
    query = parse_qs(urlparse(href).query)
    return query.get("edit_domain_id", [""])[0]

def save_json(items):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(items, file, indent=2, ensure_ascii=False)

def run_scraper():
    all_domains = []
    a = 1
    while True:
        req = session.get(URL + str(a) + ".html", timeout=15)
        print(f"Page {a}: HTTP {req.status_code} | {len(req.text)} bytes")

        if req.status_code != 200:
            print(f"FAILED PAGE {a}")
            continue

        raw = req.text
        soup = BeautifulSoup(raw, "html.parser")
        count = 0

        for element in soup.find_all("a"):

            href = element.get("href", "")
            domain = element.get_text(strip=True)

            if "/subdomain/" in href and domain != "Subdomains":

                domain_id = get_domain_id(href)
                row = element.parent.parent
                cells = row.find_all("td")

                status = cells[1].get_text(strip=True)
                age = cells[3].get_text(strip=True)

                all_domains.append({
                    "domain": domain,
                    "id": domain_id,
                    "status": status,
                    "age": age,
                })
                count += 1

        if count == 0:
            print("No domains found. ENDING SCRAPER")
            break

        print(f"Page {a}: Appended {count} domains")
        if count == 0:
            print(raw)
        
        a += 1
        
        time.sleep(0.1)

    if a < 150:
        print(f"Only reached page {a}, something is wrong. Not saving.")
        sys.exit(1)

    save_json(all_domains)
    print(f"Done. {len(all_domains)} domains saved to {OUTPUT_FILE}")

run_scraper()