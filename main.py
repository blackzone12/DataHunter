#!/usr/bin/env python3
import argparse, json, sys
from modules.core import DataHunter, console

from dotenv import load_dotenv
import os

def main():
    load_dotenv() # Load API keys from .env
    parser = argparse.ArgumentParser(description='🕵️ DataHunter - Cross-platform OSINT')
    parser.add_argument('target', nargs='?', help='Username/Phone/Image path/IP')
    parser.add_argument('--type', choices=['username', 'phone', 'ip', 'trace', 'phone-owner', 'truecaller'], default='username')
    args = parser.parse_args()
    
    if not args.target:
        parser.print_help()
        return

    hunter = DataHunter()
    results = None
    
    if args.type == 'username':
        results = hunter.search_username(args.target)
    elif args.type == 'phone':
        results = hunter.phone_lookup(args.target)
    elif args.type == 'ip':
        results = hunter.ip_intelligence(args.target)
    elif args.type == 'trace':
        results = hunter.ip_trace(args.target)
    elif args.type == 'phone-owner':
        results = hunter.phone_owner(args.target)
    elif args.type == 'truecaller':
        results = hunter.truecaller_lookup(args.target)

    if results:
        console.print(json.dumps(results, indent=2))
        file_path = hunter.save_results(args.target, results)
        console.print(f"\n[bold green][+][/bold green] Results saved to: [bold]{file_path}[/bold]")

if __name__ == '__main__':
    main()
