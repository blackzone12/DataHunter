import os, requests, json, phonenumbers
from urllib.parse import quote
from phonenumbers import geocoder, carrier
from modules import social
from rich.console import Console

console = Console()

class DataHunter:
    def __init__(self):
        self.base_dir = os.path.expanduser("~/.datahunter")
        os.makedirs(self.base_dir, exist_ok=True)
    
    def search_username(self, username):
        """Search username across platforms"""
        console.print(f"🔍 Searching '[bold cyan]{username}[/bold cyan]' across platforms...")
        
        # Load sites from JSON
        sites_path = os.path.join("modules", "sites.json")
        try:
            with open(sites_path, "r") as f:
                sites = json.load(f)
        except Exception as e:
            console.print(f"[red][!][/red] Error loading sites.json: {e}")
            return {}
        
        from concurrent.futures import ThreadPoolExecutor
        
        def check_site(name, template):
            url = template.format(username)
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                r = requests.get(url, headers=headers, timeout=5)
                if r.status_code == 200:
                    return name, url
            except:
                pass
            return name, None

        results = {}
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(check_site, name, template) for name, template in sites.items()]
            for future in futures:
                name, url = future.result()
                if url:
                    results[name] = url
        
        # Add Search Engine fallback
        results['google_search'] = f"https://www.google.com/search?q={quote(username)}"
        results['duckduckgo_search'] = f"https://duckduckgo.com/?q={quote(username)}"
        
        # Add social recon module integration
        recon = social.SocialRecon()
        twitter_data = recon.twitter_search(username)
        if twitter_data.get('status') == 'active':
             results['twitter'] = f"https://twitter.com/{username}"
        
        return results
    
    def phone_lookup(self, phone):
        """Advanced phone intelligence with HLR & GPS Tracking"""
        console.print(f"📡 [bold yellow]TRACKING[/bold yellow] phone: [bold cyan]{phone}[/bold cyan]...")
        
        from modules.phone_tracker import PhoneTracker
        tracker = PhoneTracker()
        
        # 1. Advanced HLR & GPS Intel
        intel = tracker.full_phone_intel(phone)
        
        # 2. Traditional OSINT Search Links
        clean_number = "".join(filter(str.isdigit, phone))
        search_links = {
            'truecaller': f"https://www.truecaller.com/search/global/{clean_number}",
            'sync_me': f"https://sync.me/search/?number={clean_number}",
            'facebook': f"https://www.facebook.com/search/top/?q={quote(phone)}",
            'google_dork': f"https://www.google.com/search?q=\"{quote(phone)}\" OR \"{quote(clean_number)}\""
        }

        # 3. Handle Map Generation
        results = {**intel, 'global_search_links': search_links}
        
        if 'gps' in intel and 'lat' in intel['gps']:
            map_path = tracker.generate_map(intel['gps']['lat'], intel['gps']['lon'], clean_number)
            if map_path:
                results['map_preview'] = map_path

        return results

    def ip_intelligence(self, ip):
        """Advanced Multi-Location IP tracking"""
        from modules.ip_geoloc import MultiIPGeolocator
        locator = MultiIPGeolocator()
        return locator.query_all_apis(ip)

    def ip_trace(self, ip):
        """Hop-by-hop IP trace with geolocation"""
        from modules.ip_geoloc import MultiIPGeolocator
        locator = MultiIPGeolocator()
        return locator.trace_route(ip)

    def phone_owner(self, phone):
        """Detailed owner name and address lookup"""
        from modules.phone_owner import PhoneOwnerTracker
        tracker = PhoneOwnerTracker()
        return tracker.full_owner_lookup(phone)

    def truecaller_lookup(self, phone):
        """Standalone Truecaller web scan"""
        from modules.truecaller import TruecallerTracker
        tracker = TruecallerTracker()
        return tracker.full_scan(phone)

    def save_results(self, target, data):
        """Save results to a JSON file in a 'results' folder"""
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Clean target name for filename
        clean_target = "".join(x for x in target if x.isalnum() or x in "._-")
        filename = os.path.join(results_dir, f"{clean_target}_results.json")
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        return filename
