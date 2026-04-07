import requests
from bs4 import BeautifulSoup
import re
import cloudscraper

class SMSScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://receive-smss.com"

    def get_latest_numbers(self):
        """Fetches the latest available numbers from the homepage."""
        try:
            response = self.scraper.get(self.base_url, timeout=10)
            if response.status_code != 200:
                print(f"Error fetching homepage: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            # The structure seems to be links with numbers in the text
            # and href starting with /sms/
            numbers = []
            
            # Find all links that start with /sms/
            links = soup.select("a[href^='/sms/']")
            seen_nums = set()

            for link in links:
                href = link['href']
                text = link.get_text(separator=" ", strip=True)
                
                # Extract number from href or text
                # href example: /sms/13802603245/
                match = re.search(r'/sms/(\d+)/', href)
                if match:
                    num_id = match.group(1)
                    if num_id in seen_nums:
                        continue
                    seen_nums.add(num_id)
                    
                    # Try to separate number and country from text
                    # Text example: "+13802603245 United States"
                    # We'll just take the whole text as "info" and the num_id as "number"
                    numbers.append({
                        "number": f"+{num_id}",
                        "country": text.replace(f"+{num_id}", "").strip(),
                        "link": f"{self.base_url}{href}"
                    })
            
            return numbers
        except Exception as e:
            print(f"Scraper error (Numbers): {e}")
            return []

    def get_messages(self, number_url):
        """Fetches the latest messages for a specific number."""
        try:
            response = self.scraper.get(number_url, timeout=10)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            # Messages are often in a table
            # If #msgtbl fails, look for any table
            msg_rows = soup.select("#msgtbl tbody tr") or soup.select("table tr")
            messages = []

            for row in msg_rows:
                cols = row.find_all(["td", "div"]) # Some sites use divs in rows
                if len(cols) >= 3:
                    sender = cols[0].get_text(strip=True)
                    time_ago = cols[1].get_text(strip=True)
                    text = cols[2].get_text(strip=True)
                    
                    # Sanity check: if text is empty, it might be a header or decor
                    if text and sender != "From":
                        messages.append({
                            "sender": sender,
                            "time": time_ago,
                            "text": text
                        })
            return messages
        except Exception as e:
            print(f"Scraper error (Messages): {e}")
            return []

if __name__ == "__main__":
    s = SMSScraper()
    nums = s.get_latest_numbers()
    print(f"Found {len(nums)} numbers.")
    if nums:
        print(f"First number: {nums[0]['number']}")
        msgs = s.get_messages(nums[0]['link'])
        print(f"Found {len(msgs)} messages.")
