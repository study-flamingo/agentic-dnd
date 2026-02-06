#!/bin/bash
#
# verify.sh - Verify a random.org signed dice roll
#
# Usage: ./verify.sh <random_json_file> <signature_file>
#    OR: ./verify.sh --inline '<random_json>' '<signature>'
#
# Examples:
#   ./verify.sh random.json signature.txt
#   ./verify.sh --inline '{"method":"generateSignedIntegers",...}' 'abc123...'
#
# This script calls random.org's verifySignature API to confirm
# that a dice roll is authentic and untampered.
#

set -e

# Parse arguments
if [ "$1" == "--inline" ]; then
    RANDOM_OBJ="$2"
    SIGNATURE="$3"
elif [ -f "$1" ] && [ -f "$2" ]; then
    RANDOM_OBJ=$(cat "$1")
    SIGNATURE=$(cat "$2")
else
    echo "Usage: $0 <random_json_file> <signature_file>" >&2
    echo "   OR: $0 --inline '<random_json>' '<signature>'" >&2
    exit 1
fi

# Build the verification request
# Note: We need to carefully construct the JSON to preserve the random object structure
PAYLOAD=$(jq -n \
    --argjson random "$RANDOM_OBJ" \
    --arg signature "$SIGNATURE" \
    '{
        jsonrpc: "2.0",
        method: "verifySignature",
        params: {
            random: $random,
            signature: $signature
        },
        id: 1
    }')

# Make the API call
RESPONSE=$(curl -s -X POST https://api.random.org/json-rpc/4/invoke \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

# Check for errors
if echo "$RESPONSE" | grep -q '"error"'; then
    echo "❌ VERIFICATION FAILED" >&2
    echo "" >&2
    echo "Error from random.org:" >&2
    echo "$RESPONSE" | jq -r '.error.message // .error' >&2
    exit 1
fi

# Check authenticity
AUTHENTIC=$(echo "$RESPONSE" | jq -r '.result.authenticity')

echo "═══════════════════════════════════════════════════════════════"
if [ "$AUTHENTIC" == "true" ]; then
    echo "✅ VERIFICATION PASSED"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "This roll is AUTHENTIC."
    echo ""
    echo "The signature confirms:"
    echo "  • The dice results are genuine random.org output"
    echo "  • The data has not been modified since generation"
    echo "  • The roll was made by the claimed API key holder"
    echo ""
    echo "Roll details:"
    echo "$RANDOM_OBJ" | jq '{
        dice: "\(.n)d\(.max)",
        results: .data,
        total: ([.data[]] | add),
        character: .userData.character,
        purpose: .userData.purpose,
        timestamp: .completionTime,
        serial: .serialNumber
    }'
    exit 0
else
    echo "❌ VERIFICATION FAILED"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "This roll is NOT AUTHENTIC."
    echo ""
    echo "Possible reasons:"
    echo "  • The data was modified after generation"
    echo "  • The signature was tampered with"
    echo "  • The random object and signature don't match"
    echo ""
    echo "DO NOT TRUST THIS ROLL."
    exit 1
fi
