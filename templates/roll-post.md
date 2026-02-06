# Roll Post Template

Copy and customize this template when posting your dice rolls.

> **Note on terminology:** The verification blob contains a `"random"` object and a `"signature"` — these names come from random.org's API. The "random" object holds your roll data, serial number, and metadata. The signature is random.org's cryptographic proof of authenticity.

---

## Standard Format

```markdown
**[Character]'s Roll:** [Purpose] — **[RESULT]**
Serial: #[SERIAL_NUMBER]

<details>
<summary>🔐 Verification</summary>

```json
{"random":{...},"signature":"..."}
```
</details>
```

The `roll.py` or `roll.sh` script outputs this format automatically — just copy and paste!

---

## Examples

### Single d20 Roll

```markdown
**Grognar's Roll:** Persuasion — **17**
Serial: #849

<details>
<summary>🔐 Verification</summary>

```json
{"random":{"method":"generateSignedIntegers","hashedApiKey":"abc123...","n":1,"min":1,"max":20,"data":[17],"userData":{"character":"Grognar","purpose":"Persuasion"},"serialNumber":849},"signature":"xyz789..."}
```
</details>
```

### Natural 20

```markdown
**Theron's Roll:** Attack (longsword) — **20** (NAT 20! 🎉)
Serial: #1204

<details>
<summary>🔐 Verification</summary>

```json
{"random":{...},"signature":"..."}
```
</details>
```

### Multiple Dice (Damage)

```markdown
**Lyralei's Roll:** Damage (2d6+3) — [4, 6] = **13**
Serial: #305

<details>
<summary>🔐 Verification</summary>

```json
{"random":{...},"signature":"..."}
```
</details>
```

### Advantage Roll

```markdown
**Grimjaw's Roll:** Wisdom Save (advantage) — [8, 19] taking **19**
Serial: #91

<details>
<summary>🔐 Verification</summary>

```json
{"random":{...},"signature":"..."}
```
</details>
```

---

## What the DM Sees

When you post a roll, the DM will:

1. Copy your verification JSON blob
2. Run `dm-verify.py` with your data
3. See output like:

```json
{
  "verified": true,
  "player": "Grognar",
  "roll": [17],
  "serial": 849,
  "previousSerial": 848,
  "gap": 1,
  "suspicious": false,
  "message": "✅ Verified. Serial sequence OK."
}
```

If there's a suspicious gap before a high roll, they'll see a warning.

---

## Tips

1. **Always include the serial number** — it's visible proof of sequence
2. **Use the script output directly** — it's formatted correctly
3. **Don't modify the verification blob** — any change breaks the signature
4. **One roll per action** — batch if you know you need multiple (attack + damage)
5. **Keep verification in spoilers** — makes posts readable

---

## Troubleshooting

**"Signature verification failed"**
- The verification blob was modified or corrupted
- Copy it exactly as the script outputs it

**"Serial gap detected"**  
- You rolled multiple times before posting
- DM may ask you to explain (testing is fine, cherry-picking isn't)

**"Serial went backwards"**
- Something weird happened — likely a copy-paste error
- Re-roll and post the fresh result
