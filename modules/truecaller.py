#!/usr/bin/env python3
import requests, json, subprocess, re, os
from phonenumbers import parse, format_number, PhoneNumberFormat

class TruecallerTracker:
    def __init__(self):
        self.apis = {
            'truecaller_py': self.truecaller_python_api,
            'calltracer': self.calltracer_api,
            'emobiletracker': self.emobiletracker_scrape,
            'ipqs_caller': self.ipquality_caller
        }
    
    def truecaller_python_api(self, phone):
        """Official API bridge via truecallerpy"""
        try:
            import truecallerpy
            # Note: This usually requires an installationId/token 
            # If not logged in, it will fail gracefully
            result = truecallerpy.search.retrieve(phone, "IN")
            data = result.get('data', [{}])[0]
            return {
                'name': data.get('name'),
                'location': data.get('addresses', [{}])[0].get('city'),
                'source': 'Truecaller API'
            }
        except:
            return None
    
    def calltracer_api(self, phone):
        """CallTracer.in - High Success for India"""
        try:
            parsed = parse(phone, "IN")
            number = format_number(parsed, PhoneNumberFormat.NATIONAL).replace(" ", "")
            if number.startswith('0'): number = number[1:]
            url = f"https://calltracer.in/mobile-number-details/{number}"
            r = requests.get(url, timeout=10)
            if 'Owner Name' in r.text:
                name = re.search(r'Owner Name[^:]*:\s*([^\n<]+)', r.text, re.I)
                location = re.search(r'Location[^:]*:\s*([^\n<]+)', r.text, re.I)
                name_val = name.group(1).strip() if name else None
                if name_val and "Google" not in name_val:
                    return {
                        'name': name_val,
                        'location': location.group(1).strip() if location else None,
                        'source': 'CallTracer'
                    }
        except:
            pass
        return None
    
    def emobiletracker_scrape(self, phone):
        """EMobileTracker Scraper"""
        try:
            parsed = parse(phone, "IN")
            number = format_number(parsed, PhoneNumberFormat.NATIONAL).replace(" ", "")
            url = f"https://www.emobiletracker.com/?phone={number}"
            r = requests.get(url, timeout=10)
            match = re.search(r'Owner Name.*?([A-Za-z\s]{3,20})', r.text, re.I | re.DOTALL)
            if match:
                name = match.group(1).strip()
                if "Location" not in name:
                    return {
                        'name': name,
                        'source': 'EMobileTracker'
                    }
        except:
            pass
        return None
    
    def ipquality_caller(self, phone):
        """IPQualityScore Caller ID Support"""
        try:
            key = os.getenv('IPQS_KEY')
            if not key: return None
            r = requests.get(f"https://api.ipqualityscore.com/v1/phone/number?phone={phone}&key={key}")
            if r.status_code == 200:
                data = r.json()
                return {
                    'name': data.get('recent_carrier'),
                    'source': 'IPQualityScore'
                }
        except:
            pass
        return None
    
    def full_scan(self, phone):
        """Execute all scanners and return consensus"""
        print(f"🔍 [bold cyan]PRO SCAN[/bold cyan] for {phone}...")
        results = {}
        names = []
        
        for name, func in self.apis.items():
            res = func(phone)
            if res and res.get('name'):
                results[name] = res
                names.append(res['name'])
        
        # Determine best guess
        best_name = max(set(names), key=names.count) if names else None
        
        return {
            'phone': phone,
            'truecaller_web': results.get('truecaller_py', {'error': 'No API Data'}),
            'fallback_sources': results,
            'summary': {
                'likely_name': best_name,
                'likely_location': next((r['location'] for r in results.values() if r.get('location')), None)
            }
        }
