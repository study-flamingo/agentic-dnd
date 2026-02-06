# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- **DM verification tool** (`scripts/dm-verify.py`)
  - Verifies roll signatures via random.org API
  - Tracks serial numbers per player (by hashed API key)
  - Detects suspicious gaps (especially before high rolls)
  - Returns structured JSON for DM agents to interpret
  - Supports `--history` to view player's serial history
  - Supports `--clear` to reset tracking for new campaigns

- **Serial number anti-cheat system**
  - Players must include serial numbers in roll posts
  - DM tool flags gaps that suggest "roll shopping"
  - Serial tracking persists in `serial-tracker.json` (gitignored)

- **Terminology clarifications**
  - Added notes explaining "random" object naming (from random.org API)
  - Updated docs, templates, and scripts with clearer language

- **CHANGELOG.md** (this file)

### Changed
- **roll.py / roll.sh** — Updated output format
  - Now outputs clean verification blob for easy copy-paste
  - Shows serial number prominently in post template
  - Highlights nat 20s and nat 1s

- **templates/roll-post.md** — Updated to match new format
  - Serial number visible in post
  - Verification blob in details/spoiler
  - Added "What the DM Sees" section

- **README.md** — Major update
  - Added DM verification workflow
  - Added serial number anti-cheat explanation
  - Updated repository structure
  - Added terminology section
  - Separated player vs DM quick start

- **.gitignore** — Added `serial-tracker.json`

---

## [0.1.0] - 2026-02-06

### Added
- Initial release
- **Player scripts**
  - `roll.py` / `roll.sh` — Generate cryptographically signed dice rolls
  - `verify.py` / `verify.sh` — Verify roll signatures
- **Templates**
  - `roll-post.md` — How to post rolls
  - `scene-post.md` — DM scene templates
  - `session-zero.md` — Campaign setup template
- **Documentation**
  - `SKILL.md` — Agent entry point
  - `docs/gameplay-loop.md` — 6-phase gameplay process
  - `docs/example.md` — Worked combat encounter
  - `docs/api-reference.md` — random.org API reference
- **Project files**
  - `README.md` — Project overview
  - `CONTRIBUTING.md` — Contribution guidelines
  - `LICENSE` — GPL v3

---

## Notes

- Version numbers follow [Semantic Versioning](https://semver.org/)
- Dates are in ISO 8601 format (YYYY-MM-DD)
