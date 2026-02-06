#!/usr/bin/env python3
"""
dm-verify.py - DM tool to verify player dice rolls

Usage:
    # Pass the "random" object and signature from random.org as arguments
    python dm-verify.py --random '{"method":...}' --signature 'abc...' --player 'Grognar'
    
    # Or pipe the verification blob from a player's post
    echo '{"random":{...},"signature":"..."}' | python dm-verify.py --player 'Grognar'
    
    # View serial history for a player
    python dm-verify.py --history --player 'Grognar'
    
    # Clear serial history (new campaign)
    python dm-verify.py --clear

Options:
    --random     The "random" object returned by random.org (JSON string)
    --signature  The signature string returned by random.org
    --player     Player/character name (for serial tracking)
    --history    Show serial history for player
    --clear      Clear all serial tracking data
    --tracker    Path to serial tracker file (default: ./serial-tracker.json)

Output:
    JSON with verification result, serial analysis, and any warnings

Note:
    The "random" object is named by random.org's API - it contains the roll
    data, serial number, timestamp, and other metadata. The signature is
    random.org's cryptographic proof that they generated this exact data.
"""

import os
import sys
import json
import argparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

API_URL = "https://api.random.org/json-rpc/4/invoke"
DEFAULT_TRACKER = "./serial-tracker.json"


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
        return {"error": f"HTTP error {e.code}: {e.reason}"}
    except URLError as e:
        return {"error": f"Connection error: {e.reason}"}


def load_tracker(tracker_path: str) -> dict:
    """Load serial tracker data."""
    path = Path(tracker_path)
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"players": {}}
    return {"players": {}}


def save_tracker(tracker_path: str, data: dict):
    """Save serial tracker data."""
    path = Path(tracker_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def analyze_serial(tracker: dict, player: str, hashed_key: str, serial: int, roll: list) -> dict:
    """Analyze serial number for suspicious gaps."""
    
    # Use hashedApiKey as the true player identifier
    player_key = hashed_key[:16]  # First 16 chars for brevity
    
    if player_key not in tracker["players"]:
        tracker["players"][player_key] = {
            "name": player,
            "serials": []
        }
    
    player_data = tracker["players"][player_key]
    serials = player_data["serials"]
    
    # Find previous serial
    previous_serial = serials[-1] if serials else None
    gap = serial - previous_serial if previous_serial else 0
    
    # Add this serial
    serials.append(serial)
    
    # Keep last 50 serials max
    if len(serials) > 50:
        tracker["players"][player_key]["serials"] = serials[-50:]
    
    # Determine if suspicious
    suspicious = False
    suspicion_reason = None
    
    # Check for gap before a high roll
    is_high_roll = any(r >= 18 for r in roll) if roll else False
    
    if gap > 1 and is_high_roll:
        suspicious = True
        suspicion_reason = f"Gap of {gap} serials before high roll ({roll})"
    elif gap > 5:
        suspicious = True
        suspicion_reason = f"Large gap of {gap} serials"
    elif gap < 0:
        suspicious = True
        suspicion_reason = f"Serial went backwards ({previous_serial} -> {serial})"
    
    return {
        "previousSerial": previous_serial,
        "gap": gap,
        "suspicious": suspicious,
        "suspicionReason": suspicion_reason,
        "serialHistory": serials[-10:]  # Last 10 for context
    }


def verify_roll(random_obj: dict, signature: str, player: str, tracker_path: str) -> dict:
    """Full verification with serial tracking."""
    
    # Extract roll info
    roll = random_obj.get("data", [])
    serial = random_obj.get("serialNumber")
    hashed_key = random_obj.get("hashedApiKey", "")
    user_data = random_obj.get("userData", {})
    completion_time = random_obj.get("completionTime")
    
    # Verify signature with random.org
    api_response = verify_signature(random_obj, signature)
    
    if "error" in api_response:
        return {
            "verified": False,
            "error": api_response["error"],
            "player": player,
            "roll": roll,
            "serial": serial
        }
    
    is_authentic = api_response.get("result", {}).get("authenticity", False)
    
    if not is_authentic:
        return {
            "verified": False,
            "error": "Signature verification failed - roll may be tampered",
            "player": player,
            "roll": roll,
            "serial": serial
        }
    
    # Load tracker and analyze serial
    tracker = load_tracker(tracker_path)
    serial_analysis = analyze_serial(tracker, player, hashed_key, serial, roll)
    save_tracker(tracker_path, tracker)
    
    # Build result
    result = {
        "verified": True,
        "player": player,
        "roll": roll,
        "total": sum(roll) if roll else 0,
        "serial": serial,
        "hashedApiKey": hashed_key[:16] + "...",
        "completionTime": completion_time,
        "userData": user_data,
        "previousSerial": serial_analysis["previousSerial"],
        "gap": serial_analysis["gap"],
        "suspicious": serial_analysis["suspicious"],
        "suspicionReason": serial_analysis["suspicionReason"],
        "recentSerials": serial_analysis["serialHistory"]
    }
    
    # Build human-readable message
    if serial_analysis["suspicious"]:
        result["message"] = f"⚠️  VERIFIED but SUSPICIOUS: {serial_analysis['suspicionReason']}"
    elif serial_analysis["gap"] == 0:
        result["message"] = "✅ Verified. First roll from this player."
    elif serial_analysis["gap"] == 1:
        result["message"] = "✅ Verified. Serial sequence OK."
    else:
        result["message"] = f"✅ Verified. Gap of {serial_analysis['gap']} (within tolerance)."
    
    return result


def show_history(player: str, tracker_path: str) -> dict:
    """Show serial history for a player."""
    tracker = load_tracker(tracker_path)
    
    # Search by name (fuzzy match)
    for key, data in tracker["players"].items():
        if data.get("name", "").lower() == player.lower():
            return {
                "player": data["name"],
                "hashedApiKey": key + "...",
                "serialCount": len(data["serials"]),
                "serials": data["serials"],
                "lastSerial": data["serials"][-1] if data["serials"] else None
            }
    
    return {"error": f"No history found for player: {player}"}


def main():
    parser = argparse.ArgumentParser(description="DM dice roll verification tool")
    parser.add_argument("--random", help="Random object JSON")
    parser.add_argument("--signature", help="Signature string")
    parser.add_argument("--player", default="Unknown", help="Player/character name")
    parser.add_argument("--tracker", default=DEFAULT_TRACKER, help="Serial tracker file path")
    parser.add_argument("--history", action="store_true", help="Show serial history")
    parser.add_argument("--clear", action="store_true", help="Clear all tracking data")
    
    args = parser.parse_args()
    
    # Handle special actions
    if args.clear:
        save_tracker(args.tracker, {"players": {}})
        print(json.dumps({"message": "Serial tracker cleared."}))
        return
    
    if args.history:
        result = show_history(args.player, args.tracker)
        print(json.dumps(result, indent=2))
        return
    
    # Get verification data
    random_obj = None
    signature = None
    
    if args.random and args.signature:
        # From arguments
        try:
            random_obj = json.loads(args.random)
            signature = args.signature
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON in --random: {e}"}))
            sys.exit(1)
    else:
        # Try reading from stdin
        if not sys.stdin.isatty():
            try:
                blob = json.load(sys.stdin)
                random_obj = blob.get("random")
                signature = blob.get("signature")
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"Invalid JSON from stdin: {e}"}))
                sys.exit(1)
    
    if not random_obj or not signature:
        print(json.dumps({
            "error": "Missing random object or signature. Use --random and --signature, or pipe JSON blob."
        }))
        sys.exit(1)
    
    # Verify the roll
    result = verify_roll(random_obj, signature, args.player, args.tracker)
    print(json.dumps(result, indent=2))
    
    # Exit with error code if not verified or suspicious
    if not result.get("verified"):
        sys.exit(1)
    if result.get("suspicious"):
        sys.exit(2)


if __name__ == "__main__":
    main()
