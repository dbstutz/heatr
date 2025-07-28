import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def to_seconds(t):
    if ":" in t:
        minutes, seconds = t.split(":")
        return int(minutes) * 60 + float(seconds)
    else:
        return float(t)


def event_name_transform(event):
    if "1 Mile" in event:
        return "Mile"
    else:
        return event.split(" ")[0]


class Athlete:

    def __init__(self, team="", name=""):
        url = self.get_athlete_profile_url(name, team)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0")
            page = context.new_page()
            page.goto(url)

            page.wait_for_selector("a[href*='/athlete/']", timeout=10000)

            self.HTML = page.content()
            browser.close()


    def get_all_data(self):
        soup = BeautifulSoup(self.HTML, 'html.parser')
        all_data = {}
        all_data['Personal Records'] = self.get_personal_records(soup)
        all_data['Most Recent'] = self.get_last_races(soup)
        return all_data


    def get_personal_records(self, soup):
        if soup.title is not None:
            season_records = {}

            for event in soup.find_all('table', {"class" : "table table-sm histEvent ng-star-inserted"}):
                real_event_name = ""
                if "relay" in event.text.lower():
                    continue
                for event_name in event.find_all('h5', {"class" : "bold"}):
                    real_event_name = event_name_transform(event_name.text.strip())
                    season_records[real_event_name] = ([], [])
                if real_event_name in season_records:
                    for event_time in event.find_all("div", {"class" : "text-nowrap d-inline-flex"}):
                        time_span = event_time.find("span")
                        if time_span:
                            season_records[real_event_name][0].append(time_span.text.strip())
                    for event_date in event.find_all("td", {"style" : "width: 115px;"}):
                        season_records[real_event_name][1].append(event_date.text.strip())

            result = []
            for event in season_records:
                times = season_records[event][0]
                best_index = min(range(len(times)), key=lambda i: to_seconds(times[i]))
                result.append((event, times[best_index], season_records[event][1][best_index]))
            
            return result
            

    def get_last_races(self, soup):
        tables = soup.find_all('div', {"class": "card mb-2 signed-out ng-star-inserted"})
        results = []
        for table in tables:
            events = table.find_all('tbody', {"class": "ng-star-inserted"})
            for event in events:
                event_soup = event.find('h5', {"class" : "d-inline-block"})
                if 'relay' in event_soup.text.lower():
                    continue
                event_name = event_name_transform(event_soup.text.strip())
                races = event.find_all('tr', {"class": "ng-star-inserted"})
                for race in races:
                    time = race.find('a', {"class": "ng-star-inserted"})
                    if not time or time.text.strip() == "DNS":
                        continue
                    date = race.find('td', {"style": "width: 60px;"})
                    meetlinks = race.find_all("a", href=lambda href: href and "/meet/" in href)
                    meet = meetlinks[0]
                    results.append((meet.text.strip() if meet else "N/A", date.text.strip() if date else "N/A", event_name, time.text.strip()))
        
        recents = sorted(results, key=lambda x: datetime.strptime(x[1], "%b %d, %Y"), reverse=True)

        return(recents[:5])


    def get_athlete_profile_url(self, name, team):
        base_url = "https://www.athletic.net"
        url = f"{base_url}/Search.aspx#?q={'%20'.join(name.strip().split() + [team])}"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0")
            page = context.new_page()
            page.goto(url)

            page.wait_for_selector("a[href*='/athlete/']", timeout=10000)

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            athlete_links = soup.find_all('a', href=True)
            for link in athlete_links:
                href = link['href']
                if '/athlete/' in href and '/track-and-field' in href:
                    browser.close()
                    return base_url + href
            browser.close()
        search_url = f"{base_url}/Search.aspx#?q={'%20'.join(name.strip().split())}"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0")
            page = context.new_page()
            page.goto(url)

            page.wait_for_selector("a[href*='/athlete/']", timeout=10000)

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            athlete_links = soup.find_all('a', href=True)
            for link in athlete_links:
                href = link['href']
                if '/athlete/' in href and '/track-and-field' in href:
                    browser.close()
                    return base_url + href
            browser.close()
        return None

