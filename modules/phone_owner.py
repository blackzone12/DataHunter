#!/usr/bin/env python3
import requests, phonenumbers, json, re, os
from phonenumbers import parse, geocoder, carrier

class PhoneOwnerTracker:
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or {
            'ipqs': os.getenv('IPQS_KEY'),
            'numverify': os.getenv('NUMVERIFY_KEY')
        }
    
    def calltracer_lookup(self, phone):
        """Indian mobile owner details (name + address)"""
        try:
            # Clean number for Indian service
            clean_phone = re.sub(r'[^\d]', '', phone)
            if clean_phone.startswith('91'): clean_phone = clean_phone[2:]
            
            url = f"https://calltracer.in/mobile-number-details/{clean_phone}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            if r.status_code == 200:
                # Basic parsing for demo - in production use BeautifulSoup
                name = re.search(r'Owner Name[:\s]*([^\n<]+)', r.text)
                location = re.search(r'Location[:\s]*([^\n<]+)', r.text)
                if name or location:
                    return {
                        'name': name.group(1).strip() if name else "Unknown",
                        'location': location.group(1).strip() if location else "Unknown",
                        'source': 'CallTracer.in'
                    }
        except:
            pass
        return None
    
    def whitepages_reverse(self, phone):
        """US reverse phone lookup (Name + Property)"""
        try:
            us_phone = re.sub(r'[^\d]', '', phone)
            if us_phone.startswith('1'): us_phone = us_phone[1:]
            if len(us_phone) != 10: return None
            
            url = f"https://www.whitepages.com/phone/1-{us_phone}/reverse"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            # Find owner name pattern
            name_match = re.search(r'name["\']?\s*[:=>\s]*["\']?([^<"\']+)', r.text, re.I)
            if name_match:
                return {
                    'owner_name': name_match.group(1).strip(),
                    'source': 'Whitepages'
                }
        except:
            pass
        return None
    
    def full_owner_lookup(self, phone):
        """Complete owner intelligence"""
        try:
            parsed = parse(phone, None)
            country = phonenumbers.region_code_for_number(parsed)
            
            results = {
                'phone': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'country': country,
                'basic': {
                    'carrier': carrier.name_for_number(parsed, 'en'),
                    'location': geocoder.description_for_number(parsed, 'en')
                },
                'owner_details': []
            }
            
            # Regional routing
            if country == 'IN':
                owner = self.calltracer_lookup(phone)
                if owner: results['owner_details'].append(owner)
            elif country == 'US':
                owner = self.whitepages_reverse(phone)
                if owner: results['owner_details'].append(owner)
            
            # Generic fallback (IPQS if key exists)
            if self.api_keys.get('ipqs'):
                r = requests.get(f"https://api.ipqualityscore.com/v1/phone/number?phone={phone}&key={self.api_keys['ipqs']}")
                if r.status_code == 200:
                    data = r.json()
                    results['owner_details'].append({
                        'line_type': data.get('line_type'),
                        'risk_score': data.get('abuse_score'),
                        'source': 'IPQualityScore'
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
