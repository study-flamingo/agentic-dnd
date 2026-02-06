#!/usr/bin/env python3
"""
verify.py - Verify a random.org signed dice roll

Usage:
    python verify.py <random_json_file> <signature_file>
    python verify.py --inline '<random_json>' '<signature>'
    python verify.py --json '<full_verification_json>'

Examples:
    python verify.py random.json signature.txt
    python verify.py --inline '{"method":"generateSignedIntegers",...}' 'abc123...'
    python verify.py --json '{"random":{...},"signature":"..."}'

This script calls random.org's verifySignature API to confirm
that a dice roll is authentic and untampered.
"""

import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

API_URL = "https://api.random.org/json-rpc/4/invoke"


def verify_signature(random_obj: dict, signature: str) -> dict:
    """Verify a signature using random.org API."""
    
    payload = {
        "jsonrpc": "2.0",
        "method": "verifySignature",
        "params": {
            "random": random_obj,
            "signature": signature
        },
        "id": 1
    }
    
    req = Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        raise RuntimeError(f"HTTP error {e.code}: {e.reason}")
    except URLError as e:
        raise RuntimeError(f"Connection error: {e.reason}")


def print_result(response: dict, random_obj: dict):
    """Print verification result."""
    
    if "error" in response:
        print("❌ VERIFICATION FAILED")
        print()
        print(f"Error: {response['error'].get('message', response['error'])}")
        return False
    
    authentic = response.get("result", {}).get("authenticity", False)
    
    print("═" * 65)
    if authentic:
        print("✅ VERIFICATION PASSED")
        print("═" * 65)
        print()
        print("This roll is AUTHENTIC.")
        print()
        print("The signature confirms:")
        print("  • The dice results are genuine random.org output")
        print("  • The data has not been modified since generation")
        print("  • The roll was made by the claimed API key holder")
        print()
        
        # Extract and display roll details
        data = random_obj.get("data", [])
        n = random_obj.get("n", len(data))
        max_val = random_obj.get("max", "?")
        user_data = random_obj.get("userData", {})
        
        print("Roll details:")
        print(f"  Dice:      {n}d{max_val}")
        print(f"  Results:   {data}")
        print(f"  Total:     {sum(data) if data else 'N/A'}")
        
        if user_data:
            if "character" in user_data:
                print(f"  Character: {user_data['character']}")
            if "purpose" in user_data:
                print(f"  Purpose:   {user_data['purpose']}")
        
        print(f"  Timestamp: {random_obj.get('completionTime', 'N/A')}")
        print(f"  Serial:    {random_obj.get('serialNumber', 'N/A')}")
        
        return True
    else:
        print("❌ VERIFICATION FAILED")
        print("═" * 65)
        print()
        print("This roll is NOT AUTHENTIC.")
        print()
        print("Possible reasons:")
        print("  • The data was modified after generation")
        print("  • The signature was tampered with")
        print("  • The random object and signature don't match")
        print()
        print("DO NOT TRUST THIS ROLL.")
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    random_obj = None
    signature = None
    
    # Parse arguments
    if sys.argv[1] == "--inline":
        if len(sys.argv) < 4:
            print("Error: --inline requires <random_json> <signature>", file=sys.stderr)
            sys.exit(1)
        try:
            random_obj = json.loads(sys.argv[2])
            signature = sys.argv[3]
        except json.JSONDecodeError as e:
            print(f"Error parsing random JSON: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif sys.argv[1] == "--json":
        if len(sys.argv) < 3:
            print("Error: --json requires <verification_json>", file=sys.stderr)
            sys.exit(1)
        try:
            data = json.loads(sys.argv[2])
            random_obj = data["random"]
            signature = data["signature"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        # File mode
        if len(sys.argv) < 3:
            print("Error: requires <random_file> <signature_file>", file=sys.stderr)
            sys.exit(1)
        try:
            with open(sys.argv[1]) as f:
                random_obj = json.load(f)
            with open(sys.argv[2]) as f:
                signature = f.read().strip()
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error parsing random JSON file: {e}", file=sys.stderr)
            sys.exit(1)
    
    try:
        response = verify_signature(random_obj, signature)
        success = print_result(response, random_obj)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
