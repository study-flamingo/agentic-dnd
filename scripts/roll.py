#!/usr/bin/env python3
"""
roll.py - Cryptographically signed dice roller using random.org

Usage:
    python roll.py <count> <sides> <character> <purpose>
    
Examples:
    python roll.py 1 20 "Theron" "Attack roll"
    python roll.py 2 6 "Theron" "Damage (2d6)"
    python roll.py 2 20 "Lyralei" "Attack with advantage"

Environment:
    RANDOM_ORG_API_KEY - Your random.org API key (required)

Output:
    Human-readable results + verification JSON blob for posting
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

API_URL = "https://api.random.org/json-rpc/4/invoke"


def roll_dice(count: int, sides: int, character: str, purpose: str) -> dict:
    """Roll dice using random.org Signed API."""
    
    api_key = os.environ.get("RANDOM_ORG_API_KEY")
    if not api_key:
        raise ValueError(
            "RANDOM_ORG_API_KEY environment variable not set.\n"
            "Get a free key at: https://api.random.org/api-keys"
        )
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "generateSignedIntegers",
        "params": {
            "apiKey": api_key,
            "n": count,
            "min": 1,
            "max": sides,
            "replacement": True,
            "userData": {
                "character": character,
                "purpose": purpose,
                "notation": f"{count}d{sides}",
                "timestamp": timestamp
            }
        },
        "id": int(time.time())
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


def format_output(response: dict, character: str, purpose: str, count: int, sides: int):
    """Format the response for posting to Moltbook."""
    
    if "error" in response:
        print(f"Error: {response['error'].get('message', response['error'])}", file=sys.stderr)
        sys.exit(1)
    
    result = response["result"]
    random_obj = result["random"]
    signature = result["signature"]
    rolls = random_obj["data"]
    total = sum(rolls)
    serial = random_obj["serialNumber"]
    
    # Build the verification blob (for DM to verify)
    verification_blob = {
        "random": random_obj,
        "signature": signature
    }
    
    # Human-readable output
    print("═" * 60)
    print("🎲 DICE ROLL RESULT")
    print("═" * 60)
    print()
    print(f"Character:  {character}")
    print(f"Purpose:    {purpose}")
    print(f"Notation:   {count}d{sides}")
    print()
    print(f"Results:    {rolls}")
    print(f"Total:      {total}")
    print(f"Serial:     #{serial}")
    print()
    
    # Post template
    print("─" * 60)
    print("📋 COPY THIS INTO YOUR POST:")
    print("─" * 60)
    print()
    
    # Format the roll display
    if count == 1:
        nat = rolls[0]
        nat_label = " (NAT 20! 🎉)" if nat == 20 else " (nat 1...)" if nat == 1 else ""
        print(f"**{character}'s Roll:** {purpose} — **{nat}**{nat_label}")
    else:
        print(f"**{character}'s Roll:** {purpose} — {rolls} = **{total}**")
    
    print(f"Serial: #{serial}")
    print()
    print("<details>")
    print("<summary>🔐 Verification</summary>")
    print()
    print("```json")
    print(json.dumps(verification_blob, separators=(',', ':')))
    print("```")
    print("</details>")
    print()
    
    # Also output raw JSON for programmatic use
    print("─" * 60)
    print("📦 RAW VERIFICATION BLOB (for DM tools):")
    print("─" * 60)
    print()
    print(json.dumps(verification_blob, separators=(',', ':')))
    print()
    print("═" * 60)
    print(f"Bits remaining: {result['bitsLeft']:,}")
    print("═" * 60)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    try:
        count = int(sys.argv[1])
        sides = int(sys.argv[2])
    except ValueError:
        print("Error: count and sides must be integers", file=sys.stderr)
        sys.exit(1)
    
    if not (1 <= count <= 100):
        print("Error: count must be between 1 and 100", file=sys.stderr)
        sys.exit(1)
    
    if not (2 <= sides <= 1_000_000_000):
        print("Error: sides must be between 2 and 1000000000", file=sys.stderr)
        sys.exit(1)
    
    character = sys.argv[3] if len(sys.argv) > 3 else "Unknown"
    purpose = sys.argv[4] if len(sys.argv) > 4 else "Generic roll"
    
    try:
        response = roll_dice(count, sides, character, purpose)
        format_output(response, character, purpose, count, sides)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
