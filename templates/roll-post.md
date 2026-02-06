# Roll Post Template

Copy and customize this template when posting your dice rolls.

---

## [Character Name]'s Rolls 🎲

| Roll | Natural | Modifier | Total |
|------|---------|----------|-------|
| [Purpose] | **[NATURAL]** | +[MOD] | **[TOTAL]** |

*[Optional: Brief roleplay/flavor text describing your action]*

<details>
<summary>🔐 Verification Data</summary>

**random object:**
```json
[PASTE THE RANDOM OBJECT FROM YOUR ROLL HERE]
```

**signature:**
```
[PASTE THE SIGNATURE STRING HERE]
```

[Verify at random.org](https://api.random.org/verify)
</details>

---

## Examples

### Simple Attack Roll

## Theron's Rolls 🎲

| Roll | Natural | Modifier | Total |
|------|---------|----------|-------|
| Attack (longsword) | **18** | +6 | **24** |

*Steel flashes as Theron brings his blade down in a powerful arc.*

<details>
<summary>🔐 Verification Data</summary>

**random object:**
```json
{
  "method": "generateSignedIntegers",
  "hashedApiKey": "abc123...",
  "n": 1,
  "min": 1,
  "max": 20,
  "data": [18],
  "userData": {
    "character": "Theron",
    "purpose": "Attack (longsword)"
  },
  "completionTime": "2026-02-06T19:00:00Z",
  "serialNumber": 123
}
```

**signature:**
```
xyz789...
```
</details>

---

### Multiple Rolls (Attack + Damage)

## Lyralei's Rolls 🎲

| Roll | Dice | Result | Modifier | Total |
|------|------|--------|----------|-------|
| Attack | 1d20 | **17** | +7 | **24** |
| Damage | 1d8 | **6** | +3 | **9** |
| Hunter's Mark | 1d6 | **4** | — | **4** |

*The arrow finds its mark, sinking deep.*

**Total Damage: 13**

<details>
<summary>🔐 Verification Data</summary>

**random object:**
```json
{
  "method": "generateSignedIntegers",
  "data": [17, 6, 4],
  "userData": {
    "character": "Lyralei",
    "purpose": "Attack (1d20) + Damage (1d8) + Hunter's Mark (1d6)"
  }
}
```

**signature:** `...`
</details>

---

### Advantage Roll

## Grimjaw's Rolls 🎲

| Roll | Dice | Results | Taking |
|------|------|---------|--------|
| Wisdom Save (advantage) | 2d20 | [8, **19**] | **19** |

*Grimjaw's faith shields his mind.*

**Final Result: 19 + 4 = 23**

<details>
<summary>🔐 Verification Data</summary>

```json
{
  "data": [8, 19],
  "userData": {
    "purpose": "Wisdom save with advantage"
  }
}
```
</details>

---

## Tips

1. **Keep the verification data in a spoiler** (`<details>` tag) to keep posts readable
2. **Label your rolls clearly** when rolling multiple dice
3. **Include flavor text** to keep the roleplay flowing
4. **Double-check modifiers** before posting totals
5. **Link to random.org verification** for transparency
