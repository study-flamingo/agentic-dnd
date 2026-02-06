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
#   JSON response with dice results and cryptographic signature
#   Ready to copy into Moltbook post verification section
#

set -e

# Check for API key
if [ -z "$RANDOM_ORG_API_KEY" ]; then
    echo "Error: RANDOM_ORG_API_KEY environment variable not set" >&2
    echo "Get a free key at: https://api.random.org/api-keys" >&2
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
if echo "$RESPONSE" | grep -q '"error"'; then
    echo "Error from random.org:" >&2
    echo "$RESPONSE" | jq -r '.error.message // .error' >&2
    exit 1
fi

# Extract and display results
echo "═══════════════════════════════════════════════════════════════"
echo "🎲 DICE ROLL RESULT"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Character: $CHARACTER"
echo "Purpose:   $PURPOSE"
echo "Notation:  ${COUNT}d${SIDES}"
echo ""

# Show the actual rolls
ROLLS=$(echo "$RESPONSE" | jq -r '.result.random.data | @csv' | tr ',' ' ')
echo "Results:   [ $ROLLS ]"

# Calculate total
TOTAL=$(echo "$RESPONSE" | jq '[.result.random.data[]] | add')
echo "Total:     $TOTAL"

echo ""
echo "───────────────────────────────────────────────────────────────"
echo "📋 VERIFICATION DATA (copy this into your post)"
echo "───────────────────────────────────────────────────────────────"
echo ""
echo "**random object:**"
echo '```json'
echo "$RESPONSE" | jq '.result.random'
echo '```'
echo ""
echo "**signature:**"
echo '```'
echo "$RESPONSE" | jq -r '.result.signature'
echo '```'
echo ""
echo "───────────────────────────────────────────────────────────────"
echo "Serial #$(echo "$RESPONSE" | jq -r '.result.random.serialNumber') | $(echo "$RESPONSE" | jq -r '.result.random.completionTime')"
echo "Bits remaining: $(echo "$RESPONSE" | jq -r '.result.bitsLeft')"
echo "═══════════════════════════════════════════════════════════════"
