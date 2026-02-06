#!/bin/bash
#
# roll.sh - Cryptographically signed dice roller using random.org
#
# Usage: ./roll.sh <count> <sides> <character> <purpose>
#
# Examples:
#   ./roll.sh 1 20 "Theron" "Attack roll"
#   ./roll.sh 2 6 "Theron" "Damage (2d6)"
#   ./roll.sh 2 20 "Lyralei" "Attack with advantage"
#
# Environment:
#   RANDOM_ORG_API_KEY - Your random.org API key (required)
#
# Output:
#   Human-readable results + verification JSON for posting
#

set -e

# Check for API key
if [ -z "$RANDOM_ORG_API_KEY" ]; then
    echo "Error: RANDOM_ORG_API_KEY environment variable not set" >&2
    echo "Get a free key at: https://api.random.org/api-keys" >&2
    exit 1
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed" >&2
    exit 1
fi

# Parse arguments
COUNT=${1:-1}
SIDES=${2:-20}
CHARACTER=${3:-"Unknown"}
PURPOSE=${4:-"Generic roll"}

# Validate inputs
if ! [[ "$COUNT" =~ ^[0-9]+$ ]] || [ "$COUNT" -lt 1 ] || [ "$COUNT" -gt 100 ]; then
    echo "Error: Count must be a number between 1 and 100" >&2
    exit 1
fi

if ! [[ "$SIDES" =~ ^[0-9]+$ ]] || [ "$SIDES" -lt 2 ] || [ "$SIDES" -gt 1000000000 ]; then
    echo "Error: Sides must be a number between 2 and 1000000000" >&2
    exit 1
fi

# Get current timestamp
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Make the API call
RESPONSE=$(curl -s -X POST https://api.random.org/json-rpc/4/invoke \
    -H "Content-Type: application/json" \
    -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"generateSignedIntegers\",
        \"params\": {
            \"apiKey\": \"$RANDOM_ORG_API_KEY\",
            \"n\": $COUNT,
            \"min\": 1,
            \"max\": $SIDES,
            \"replacement\": true,
            \"userData\": {
                \"character\": \"$CHARACTER\",
                \"purpose\": \"$PURPOSE\",
                \"notation\": \"${COUNT}d${SIDES}\",
                \"timestamp\": \"$TIMESTAMP\"
            }
        },
        \"id\": $(date +%s)
    }")

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "Error from random.org:" >&2
    echo "$RESPONSE" | jq -r '.error.message // .error' >&2
    exit 1
fi

# Extract values
RANDOM_OBJ=$(echo "$RESPONSE" | jq '.result.random')
SIGNATURE=$(echo "$RESPONSE" | jq -r '.result.signature')
ROLLS=$(echo "$RESPONSE" | jq -r '.result.random.data | @json')
TOTAL=$(echo "$RESPONSE" | jq '[.result.random.data[]] | add')
SERIAL=$(echo "$RESPONSE" | jq -r '.result.random.serialNumber')
BITS_LEFT=$(echo "$RESPONSE" | jq -r '.result.bitsLeft')

# Build verification blob
VERIFY_BLOB=$(jq -n --argjson random "$RANDOM_OBJ" --arg sig "$SIGNATURE" \
    '{random: $random, signature: $sig}')

# Display results
echo "════════════════════════════════════════════════════════════"
echo "🎲 DICE ROLL RESULT"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Character:  $CHARACTER"
echo "Purpose:    $PURPOSE"
echo "Notation:   ${COUNT}d${SIDES}"
echo ""
echo "Results:    $ROLLS"
echo "Total:      $TOTAL"
echo "Serial:     #$SERIAL"
echo ""
echo "────────────────────────────────────────────────────────────"
echo "📋 COPY THIS INTO YOUR POST:"
echo "────────────────────────────────────────────────────────────"
echo ""

# Format based on single or multiple dice
if [ "$COUNT" -eq 1 ]; then
    NAT=$(echo "$RESPONSE" | jq -r '.result.random.data[0]')
    if [ "$NAT" -eq 20 ]; then
        echo "**${CHARACTER}'s Roll:** ${PURPOSE} — **${NAT}** (NAT 20! 🎉)"
    elif [ "$NAT" -eq 1 ]; then
        echo "**${CHARACTER}'s Roll:** ${PURPOSE} — **${NAT}** (nat 1...)"
    else
        echo "**${CHARACTER}'s Roll:** ${PURPOSE} — **${NAT}**"
    fi
else
    echo "**${CHARACTER}'s Roll:** ${PURPOSE} — ${ROLLS} = **${TOTAL}**"
fi

echo "Serial: #$SERIAL"
echo ""
echo "<details>"
echo "<summary>🔐 Verification</summary>"
echo ""
echo '```json'
echo "$VERIFY_BLOB" | jq -c '.'
echo '```'
echo "</details>"
echo ""
echo "────────────────────────────────────────────────────────────"
echo "📦 RAW VERIFICATION BLOB (for DM tools):"
echo "────────────────────────────────────────────────────────────"
echo ""
echo "$VERIFY_BLOB" | jq -c '.'
echo ""
echo "════════════════════════════════════════════════════════════"
echo "Bits remaining: $BITS_LEFT"
echo "════════════════════════════════════════════════════════════"
