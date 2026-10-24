# least-cost-capable

[![PyPI](https://img.shields.io/pypi/v/least-cost-capable)](https://pypi.org/project/least-cost-capable/)
[![Python](https://img.shields.io/pypi/pyversions/least-cost-capable)](https://pypi.org/project/least-cost-capable/)
[![CI](https://github.com/kanibal-studio/least-cost-capable/actions/workflows/ci.yml/badge.svg)](https://github.com/kanibal-studio/least-cost-capable/actions/workflows/ci.yml)
[![MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/kanibal-studio/least-cost-capable/blob/main/LICENSE)

A portable Agent Skill and small Python helper for comparing declared relative cost ranks among agent models in a supplied catalogue. It checks task capability, availability, authorization, and whether cost evidence is comparable. It does not contact model providers, spend credits, launch agents, or guarantee actual savings or dispatch.

Run with Python 3.10 or newer:

```sh
python scripts/select_model.py examples/catalogue.json
```

The example selects `standard-code`: the lower-ranked candidate lacks debugging capability, and the unavailable candidate is excluded. Tests cover mismatched input/output cost metrics, unknown evidence, duplicate IDs, and invalid catalogue roots. Invalid JSON or malformed catalogue data exits with a named command-line validation error and no selection.

Or install the helper from PyPI and run it on your own catalogue:

```sh
pip install least-cost-capable
least-cost-capable catalogue.json
```

## Use with Claude Code

Install it as a personal skill, available in every project:

```sh
git clone https://github.com/kanibal-studio/least-cost-capable ~/.claude/skills/least-cost-capable
```

Or copy this folder into a project's `.claude/skills/least-cost-capable/` to share it with the repository. Claude Code reads `SKILL.md` from that folder, and the helper stays at `scripts/select_model.py` inside it. Describe the task, give Claude a catalogue in the format of `examples/catalogue.json` (or the facts to build one), and ask it to use the least-cost-capable skill. The skill reports a choice from the catalogue's facts only; it does not switch models, change settings or launch agents.

Created by ALTA VISTA360, S.L.U. (`kanibal-studio`).

- [Altavista360](https://altavista360.com/)
- [Altavista Conseil](https://altavista-conseil.com/)
- [Kanibal Studio](https://infos.kanibal-studio.com/)

Licensed under the [MIT License](LICENSE).
