import pandas as pd
import requests
import re
import numpy as np
from bs4 import BeautifulSoup
from io import StringIO


def parseEventMark(mark):
    # try to make pandas use float to avoid importing all of numpy
    if isinstance(mark, np.float64) or isinstance(mark, float):
        return float(mark)

    # Some results are just the float
    if mark.isalpha():
        return mark

    # Possible edge case - false start with wind
    if "FS" in mark:
        return "FS"

    # possibly irrelevant
    elif mark.replace(".", "").isnumeric():
        return float(mark)

    else:
        # Don't want feet conversion or wind right now
        endChars = ["m", "W", "w", "(", "W"]
        for char in endChars:
            if char in mark:
                return float(mark[0 : mark.index(char)])

    # Unaccounted for
    return mark


def parseEventName(name):
    cleaned = str(name).replace("  ", " ") if name != "10000" else "10,000"
    return cleaned.replace(".0", "")


class Athlete:

    def __init__(self, team="", name=""):
        url = self.get_athlete_profile_url(name, team)

        if url is None:
            raise Exception(f"Could not find athlete profile for {name} from {team}")

        # Get the response
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        # Create the attributes and leave them blank
        self.data = None
        self.soup = None
        self.dfs = None

        # Handle the response
        if response.status_code < 300 and response.status_code >= 200:
            # panda's read_html doesn't accept percent colspan arguments
            self.HTML = response.text.replace('colspan="100%"', 'colspan="3"')
        else:
            self.HTML = None
            raise Exception("Could not retrieve", response.status_code)


    def get_all_data(self):
        # If not created already get the dataframes
        if not self.dfs:
            self.dfs = pd.read_html(StringIO(self.HTML))
        # Check for no personal records
        if len(self.dfs) == 0:
            return {"Has not competed": None}
        df = self.dfs[0]

        soup = BeautifulSoup(self.HTML, 'html.parser')
        all_data = {}
        all_data['Personal Records'] = self.get_personal_records(soup, df)
        all_data['Most Recent'] = self.get_last_races(soup)
        return all_data


    def get_personal_records(self, soup, df):
        table = soup.find('table')  # or refine this if there are multiple tables

        links = []
        for row in table.find_all('tr'):  # skip header
            row_links = []
            for td in row.find_all('td'):
                a = td.find('a')
                if a and 'href' in a.attrs:
                    row_links.append(a['href'])
                else:
                    row_links.append(None)
            links.append(row_links)

        numLeft = sum(pd.notnull(df.iloc[:, 0]))
        numRight = sum(pd.notnull(df.iloc[:, 2]))
        numEvents = numLeft + numRight

        PRs = np.empty([numEvents, 3], dtype=object)  # add third col for URL

        for i in range(df.shape[0]):
            PRs[i, 0] = df.iloc[i, 0]
            PRs[i, 1] = df.iloc[i, 1]
            PRs[i, 2] = links[i][1] if len(links[i]) > 1 else None

            if pd.notnull(df.iloc[i, 2]):
                PRs[i + numLeft, 0] = df.iloc[i, 2]
                PRs[i + numLeft, 1] = df.iloc[i, 3]
                PRs[i + numLeft, 2] = links[i][3] if len(links[i]) > 3 else None

        PRs = pd.DataFrame(PRs)
        PRs.columns = ["Event", "Mark", "URL"]

        PRs["Mark"] = PRs["Mark"].apply(lambda mark: parseEventMark(mark))
        for i in range(len(PRs)):
            if PRs["Event"][i] in ("HEP", "PENT", "DEC"):
                PRs.loc[i, "Mark"] = int(PRs["Mark"][i])

        PRs["Event"] = PRs["Event"].apply(parseEventName)
        PRs.set_index("Event", inplace=True)

        pr_dict = PRs.to_dict()
        result = []
        for event, time in pr_dict['Mark'].items():
            url = pr_dict['URL'][event]
            if url:
                meet_info = self.get_meet_info(url)
                meet_name, meet_date = meet_info["meet_name"], meet_info["meet_date"]
            else:
                meet_name, meet_date = "Unknown Meet", "Unknown Date"
            result.append((event, time, meet_name, meet_date))

        return result


    def get_meet_info(self, url):
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " 
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        } 
        '''

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print("Failed to fetch the page. Status code:", response.status_code)
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Get meet name
        title_tag = soup.find('h3', class_='panel-title')
        meet_name = title_tag.get_text(strip=True) if title_tag else "Unknown Meet"

        # Get date (first matching panel-heading-normal-text)
        date_div = soup.find('div', class_='panel-heading-normal-text inline-block')
        meet_date = date_div.get_text(strip=True) if date_div else "Unknown Date"

        return {
            "meet_name": meet_name,
            "meet_date": meet_date
        }


    def get_athlete_profile_url(self, name, team):
        base_url = "https://www.tfrrs.org"
        search_url = f"{base_url}/search.html?athlete={'+'.join(name.strip().split())}&team={team}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/123.0.0.0 Safari/537.36"
        }
        for i in range(2):
            try:
                response = requests.get(search_url, headers=headers)
                response.raise_for_status()
            except Exception as e:
                print(f"Search request failed: {e}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # TFRRS returns results in <a> tags with /athletes/ in href
            athlete_links = soup.find_all('a', href=True)
            for link in athlete_links:
                href = link['href']
                if '/athletes/' in href:
                    return base_url + href  # e.g., https://www.tfrrs.org/athletes/8129889/Name_Of_Athlete
            
            # Try again without team
            search_url = f"{base_url}/search.html?athlete={'+'.join(name.strip().split())}"
        return None


    def get_last_races(self, soup):
        tables = soup.find_all('table', class_=lambda x: x and 'table-hover' in x)

        events = []

        for table in tables:
            # Get meet name and date
            header = table.find('th')
            if not header:
                continue
            meet_link = header.find('a')
            meet_name = meet_link.text.strip() if meet_link else "Unknown Meet"
            date_span = header.find('span')
            meet_date = date_span.text.strip() if date_span else "Unknown Date"

            # Get the race row
            # event_rows = table.find_all('tr', class_='highlight')
            event_rows = table.find_all('tr')
            for row in event_rows:
                tds = row.find_all('td')
                if len(tds) < 2:
                    continue

                event_name = tds[0].text.strip()
                time_cell = tds[1].find('a')
                time = time_cell.text.strip() if time_cell else "Unknown Time"

                events.append((
                    meet_name,
                    meet_date,
                    event_name,
                    time
                ))

        return events[:3]

        