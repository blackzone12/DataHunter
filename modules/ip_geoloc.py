#!/usr/bin/env python3
import requests, json, concurrent.futures, os, folium
from urllib.parse import quote
from rich.console import Console

console = Console()

class MultiIPGeolocator:
    def __init__(self):
        self.apis = {
            'ip_api': "http://ip-api.com/json/{ip}?fields=status,country,regionName,city,lat,lon,isp,org,as,zip",
            'ipinfo': "https://ipinfo.io/{ip}/json",
            'ipwhois': "https://ipwhois.app/json/{ip}",
            'geoplugin': "http://www.geoplugin.net/json.gp?ip={ip}",
            'ipapi': "https://ipapi.co/{ip}/json/"
        }
    
    def query_all_apis(self, ip):
        """Query ALL APIs concurrently for maximum precision"""
        console.print(f"🌍 [bold yellow]DEEP SCAN[/bold yellow]: Querying multiple sources for {ip}...")
        
        def single_api(api_name, url_template):
            try:
                url = url_template.format(ip=ip)
                # Add token for ipinfo if available
                if api_name == 'ipinfo' and os.getenv('IPINFO_TOKEN'):
                    url += f"?token={os.getenv('IPINFO_TOKEN')}"
                
                r = requests.get(url, timeout=5, headers={'User-Agent': 'DataHunter/1.0'})
                if r.status_code == 200:
                    data = r.json()
                    if data.get('status') != 'fail' and not data.get('error'):
                        return self.normalize_data(data, api_name)
            except:
                pass
            return None
        
        # Concurrent execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(single_api, name, template) 
                for name, template in self.apis.items()
            ]
            results = [f.result() for f in concurrent.futures.as_completed(futures) if f.result()]
        
        if not results:
            return {'error': 'No location data found from any source'}
            
        return self.aggregate_results(results, ip)
    
    def normalize_data(self, data, source):
        """Standardize API responses into a common format"""
        location = {}
        
        # Handle loc: "lat,lon" from ipinfo
        if 'loc' in data:
            lat, lon = data['loc'].split(',')
            data['lat'] = lat
            data['lon'] = lon

        field_map = {
            'country': ['country', 'country_name', 'countryCode'],
            'region': ['regionName', 'region', 'region_code'],
            'city': ['city', 'locality'],
            'isp': ['isp', 'org', 'organization'],
            'lat': ['lat', 'latitude'],
            'lon': ['lon', 'longitude'],
            'zip': ['zip', 'postal']
        }
        
        for standard, variants in field_map.items():
            for variant in variants:
                if variant in data and data[variant]:
                    location[standard] = str(data[variant])
                    break
        
        location['source'] = source
        location['confidence'] = self.get_confidence(data)
        return location
    
    def get_confidence(self, data):
        """Calculate location confidence based on ISP type"""
        isp = data.get('isp', '').lower() or data.get('org', '').lower()
        if any(x in isp for x in ['google', 'cloudflare', 'amazon', 'digitalocean', 'microsoft', 'vpn', 'proxy']):
            return 'low (Datacenter/VPN)'
        elif 'mobile' in isp:
            return 'medium (Mobile Network)'
        return 'high (Static ISP)'
    
    def aggregate_results(self, results, ip):
        """Combine multiple API results and identify consensus"""
        locations = {}
        for result in results:
            key = f"{result.get('city', 'Unknown')}, {result.get('region', 'Unknown')}"
            if key not in locations:
                locations[key] = {
                    'city': result.get('city'),
                    'region': result.get('region'), 
                    'country': result.get('country'),
                    'sources': [],
                    'avg_lat': [],
                    'avg_lon': [],
                    'confidence_scores': []
                }
            locations[key]['sources'].append(result['source'])
            if result.get('lat'): locations[key]['avg_lat'].append(float(result['lat']))
            if result.get('lon'): locations[key]['avg_lon'].append(float(result['lon']))
            locations[key]['confidence_scores'].append(result['confidence'])
        
        for loc in locations.values():
            if loc['avg_lat']:
                loc['lat'] = round(sum(loc['avg_lat']) / len(loc['avg_lat']), 4)
                loc['lon'] = round(sum(loc['avg_lon']) / len(loc['avg_lon']), 4)
            loc['sources_count'] = len(loc['sources'])
            loc['google_maps'] = f"https://www.google.com/maps?q={loc.get('lat')},{loc.get('lon')}"
            
            # Save individual map for this location cluster
            self.save_map(loc.get('lat'), loc.get('lon'), ip, loc.get('city', 'Cluster'))

        return {
            'ip': ip,
            'total_sources': len(results),
            'possible_locations': list(locations.values()),
            'final_consensus': max(locations.values(), key=lambda x: x['sources_count'])
        }

    def save_map(self, lat, lon, ip, city):
        """Generate interactive HTML map"""
        if not lat or not lon: return
        try:
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], popup=f"IP: {ip}\nCity: {city}").add_to(m)
            results_dir = "results"
            os.makedirs(results_dir, exist_ok=True)
            m.save(os.path.join(results_dir, f"map_{ip.replace('.','_')}.html"))
        except:
            pass

    def trace_route(self, target_ip):
        """Trace network hops with geolocation"""
        import subprocess, platform, re
        console.print(f"🛰️  [bold yellow]TRACING[/bold yellow] path to {target_ip}...")
        
        cmd = ["tracert", "-d", target_ip] if platform.system() == "Windows" else ["traceroute", "-n", target_ip]
        hops = []
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ""):
                print(line.strip())
                match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if match:
                    hop_ip = match.group(1)
                    if hop_ip not in [target_ip, "127.0.0.1"] and not hop_ip.startswith("192.168."):
                        hops.append(hop_ip)
            process.stdout.close()
            process.wait()
        except Exception:
            pass

        trace_data = []
        for i, h_ip in enumerate(hops[:10]): # Limit to 10 hops for speed
            geo = self.query_all_apis(h_ip)
            if 'error' not in geo:
                trace_data.append({f"Hop {i+1}": geo})
        
        return trace_data
