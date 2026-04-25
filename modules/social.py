import requests
from bs4 import BeautifulSoup

class SocialRecon:
    def __init__(self):
        self.proxies = self.get_proxies()
    
    def get_proxies(self):
        """Free proxy rotation (placeholder for actual rotation logic)"""
        return [
            'http://spys.one/free-proxy-list',
            # Add more proxy sources
        ]
    
    def twitter_search(self, username):
        url = f"https://twitter.com/{username}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        try:
            r = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extract bio, followers, last active (Note: Twitter is heavily JS-reliant)
            bio = soup.find('div', {'data-testid': 'UserDescription'})
            return {
                'bio': bio.text if bio else None,
                'status': 'active' if r.status_code == 200 else 'not_found'
            }
        except:
            return {'status': 'error', 'message': 'Request failed'}
