# random.org API Reference

Quick reference for the Signed API methods used by this skill.

## Terminology Note

In this documentation and our scripts, you'll see references to:

- **"random" object** — This is the name random.org gives to the object containing your roll results, serial number, timestamp, and other metadata. It's not "random" as in arbitrary — it's the `random` field from their API response.

- **signature** — The cryptographic signature that random.org generates for the "random" object. Together, these two pieces prove the roll is authentic.

## Endpoint

```
POST https://api.random.org/json-rpc/4/invoke
Content-Type: application/json
```

## generateSignedIntegers

Generate cryptographically signed random integers.

### Request

```json
{
  "jsonrpc": "2.0",
  "method": "generateSignedIntegers",
  "params": {
    "apiKey": "your-api-key-here",
    "n": 1,
    "min": 1,
    "max": 20,
    "replacement": true,
    "userData": {
      "character": "Theron",
      "purpose": "Attack roll"
    }
  },
  "id": 12345
}
```

### Parameters

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `apiKey` | Yes | string | Your random.org API key |
| `n` | Yes | int | Number of integers (1-10000) |
| `min` | Yes | int | Minimum value (-1e9 to 1e9) |
| `max` | Yes | int | Maximum value (-1e9 to 1e9) |
| `replacement` | No | bool | Allow duplicates (default: true) |
| `base` | No | int | Number base: 2, 8, 10, 16 (default: 10) |
| `userData` | No | object | Custom data included in signature |

### Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "random": {
      "method": "generateSignedIntegers",
      "hashedApiKey": "abc123...",
      "n": 1,
      "min": 1,
      "max": 20,
      "replacement": true,
      "base": 10,
      "pregeneratedRandomization": null,
      "data": [17],
      "license": {
        "type": "developer",
        "text": "...",
        "infoUrl": null
      },
      "licenseData": null,
      "userData": {
        "character": "Theron",
        "purpose": "Attack roll"
      },
      "ticketData": null,
      "completionTime": "2026-02-06T19:00:00Z",
      "serialNumber": 12345
    },
    "signature": "base64-encoded-signature...",
    "cost": 0,
    "bitsUsed": 5,
    "bitsLeft": 999995,
    "requestsLeft": 999,
    "advisoryDelay": 1000
  },
  "id": 12345
}
```

### Response Fields

| Field | Description |
|-------|-------------|
| `random` | The signed payload containing all roll data |
| `random.data` | Array of generated integers |
| `random.hashedApiKey` | SHA-512 hash of API key (shareable) |
| `random.serialNumber` | Unique sequence number for this key |
| `random.completionTime` | UTC timestamp of generation |
| `random.userData` | Your custom data (included in signature) |
| `signature` | Base64-encoded cryptographic signature |
| `bitsLeft` | Remaining daily quota |
| `advisoryDelay` | Milliseconds to wait before next request |

---

## verifySignature

Verify that a random object and signature are authentic.

### Request

```json
{
  "jsonrpc": "2.0",
  "method": "verifySignature",
  "params": {
    "random": {
      "method": "generateSignedIntegers",
      "hashedApiKey": "abc123...",
      "n": 1,
      "min": 1,
      "max": 20,
      "replacement": true,
      "base": 10,
      "pregeneratedRandomization": null,
      "data": [17],
      "license": { ... },
      "licenseData": null,
      "userData": { ... },
      "ticketData": null,
      "completionTime": "2026-02-06T19:00:00Z",
      "serialNumber": 12345
    },
    "signature": "base64-encoded-signature..."
  },
  "id": 1
}
```

### Response (Authentic)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "authenticity": true
  },
  "id": 1
}
```

### Response (Not Authentic)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "authenticity": false
  },
  "id": 1
}
```

**Note:** The `random` object must be passed **exactly** as received, including all fields. Any modification (even whitespace in some cases) will cause verification to fail.

---

## Error Codes

| Code | Meaning |
|------|---------|
| -32600 | Invalid request |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error |
| 100 | API key not found |
| 101 | API key inactive |
| 200 | Insufficient bits (quota exceeded) |
| 201 | Insufficient requests (quota exceeded) |
| 300 | Parameter out of range |

---

## Rate Limits

**Free Developer Tier:**
- 1,000,000 bits per day
- Bits reset at midnight UTC

**Typical Usage:**
- 1d20 = ~5 bits
- 2d6 = ~6 bits
- 4d6 = ~11 bits

With 1M bits/day, you can make approximately:
- 200,000 d20 rolls
- 166,000 2d6 rolls
- 90,000 4d6 rolls

More than enough for any TTRPG campaign.

---

## Official Documentation

- API Overview: https://api.random.org/features
- Signed API: https://api.random.org/json-rpc/4/signed
- Get API Key: https://api.random.org/api-keys
- Verification Form: https://api.random.org/verify
