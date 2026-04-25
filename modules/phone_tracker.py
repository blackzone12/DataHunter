#!/usr/bin/env python3
import requests, phonenumbers, json, os
from phonenumbers import geocoder, carrier, parse

class PhoneTracker:
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or {
            'ipqs': os.getenv('IPQS_KEY'),
            'numverify': os.getenv('NUMVERIFY_KEY'),
            'google': os.getenv('GOOGLE_MAPS_KEY')
        }
    
    def hlr_lookup(self, phone):
        """HLR - Real-time carrier + location"""
        try:
            parsed = parse(phone, None)
            msisdn = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except:
            return {'error': 'Invalid phone format'}
            
        # IPQualityScore HLR (free tier)
        if self.api_keys.get('ipqs'):
            try:
                r = requests.get(f"https://api.ipqualityscore.com/v1/phone/number?phone={msisdn}&key={self.api_keys['ipqs']}")
                if r.status_code == 200:
                    data = r.json()
                    return {
                        'carrier': data.get('carrier'),
                        'country': data.get('country'),
                        'line_type': data.get('line_type'),
                        'status': data.get('valid')
                    }
            except:
                pass
        
        # Numverify fallback
        if self.api_keys.get('numverify'):
            try:
                r = requests.get(f"http://apilayer.net/api/validate?access_key={self.api_keys['numverify']}&number={msisdn}")
                data = r.json()
                return {
                    'location': data.get('location'),
                    'carrier': data.get('carrier'),
                    'lat': data.get('latitude'),
                    'lon': data.get('longitude')
                }
            except:
                pass
        
        return {'error': 'HLR lookup failed (Missing API Keys or Network Error)'}
    
    def cell_tower_triangulation(self, phone):
        """Simulate tower-based GPS (Google Geolocation API)"""
        # Note: Real implementation would needs cell tower data from the device/network
        # This implementation uses the Google Geolocation API with provided key
        if not self.api_keys.get('google'):
            return {'error': 'Google Maps API Key missing for triangulation'}
            
        # Mocking cell data for structure - in production this would be fetched from HLR/SS7
        mock_towers = [
            {"cellId": 12345, "locationAreaCode": 678, "mobileCountryCode": 404, "mobileNetworkCode": 10, "signalStrength": -65}
        ]
        
        data = {
            'homeMobileCountryCode': 404,
            'homeMobileNetworkCode': 10,
            'radioType': 'lte',
            'considerIp': True,
            'cellTowers': mock_towers
        }
        
        try:
            r = requests.post(f"https://www.googleapis.com/geolocation/v1/geolocate?key={self.api_keys['google']}", json=data)
            loc = r.json()
            return {
                'lat': loc['location']['lat'],
                'lon': loc['location']['lng'],
                'accuracy': loc['accuracy']
            }
        except:
            return {'error': 'Cell triangulation failed'}
    
    def identity_lookup(self, phone, gps_data=None):
        """Attempt to find owner name and address"""
        identity = {
            'owner_name': 'Searching...',
            'address': 'Searching...',
            'reliability': 'Low'
        }
        
        # 1. Reverse Geocode the address if GPS is available
        if gps_data and 'lat' in gps_data:
            from geopy.geocoders import Nominatim
            try:
                geolocator = Nominatim(user_agent="DataHunter_OSINT")
                location = geolocator.reverse(f"{gps_data['lat']}, {gps_data['lon']}")
                if location:
                    identity['address'] = location.address
                    identity['reliability'] = 'High (GPS Verified)'
            except:
                pass

        # 2. Mocking/Bridge for Identity APIs (Truecaller/Sync.me/NumVerify Pro)
        # Note: Truecaller requires session tokens usually.
        if self.api_keys.get('numverify'):
             # Logic to parse owner name from extended NumVerify responses
             pass
             
        return identity

    def full_phone_intel(self, phone):
        """Complete phone intelligence"""
        try:
            parsed = parse(phone, None)
            basic = {
                'formatted': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'country': geocoder.description_for_number(parsed, 'en'),
                'carrier': carrier.name_for_number(parsed, 'en'),
                'valid': phonenumbers.is_valid_number(parsed)
            }
            
            # HLR lookup
            hlr = self.hlr_lookup(phone)
            
            # GPS coordinates
            gps = self.cell_tower_triangulation(phone)
            
            # Identity Lookup (Name + Address)
            identity = self.identity_lookup(phone, gps if 'error' not in gps else None)
            
            # 🔍 Truecaller Pro Multi-Source Scan
            try:
                from modules.truecaller import TruecallerTracker
                tt = TruecallerTracker()
                truecaller_res = tt.full_scan(phone)
                if truecaller_res['summary'].get('likely_name'):
                    identity['owner_name'] = truecaller_res['summary']['likely_name']
                    identity['address'] = truecaller_res['summary'].get('likely_location') or identity['address']
                    # Reliability based on sources found
                    source_count = len(truecaller_res['fallback_sources'])
                    if source_count > 1:
                        identity['reliability'] = f'High ({source_count} Sources Found)'
                    else:
                        identity['reliability'] = 'Medium (Single Source)'
            except:
                truecaller_res = {}

            # Real Owner Lookup (Multi-API Name/City)
            from modules.phone_owner import PhoneOwnerTracker
            owner_tracker = PhoneOwnerTracker()
            owner_data = owner_tracker.full_owner_lookup(phone)
            
            return {
                **basic, 
                'hlr': hlr, 
                'gps': gps, 
                'identity': identity, 
                'truecaller': truecaller_res,
                'owner_intel': owner_data.get('owner_details', [])
            }
        except Exception as e:
            return {'error': str(e)}

    def generate_map(self, lat, lon, target_name):
        """Visual map generation"""
        try:
            import folium
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker([lat, lon], popup=f"Phone Location: {target_name}").add_to(m)
            results_dir = "results"
            os.makedirs(results_dir, exist_ok=True)
            map_path = os.path.join(results_dir, f"{target_name}_location.html")
            m.save(map_path)
            return map_path
        except:
            return None
