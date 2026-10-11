# least-cost-capable

A portable Agent Skill and small Python helper for comparing declared relative cost ranks among agent models in a supplied catalogue. It checks task capability, availability, authorization, and whether cost evidence is comparable. It does not contact model providers, spend credits, launch agents, or guarantee actual savings or dispatch.

Run with Python 3.10 or newer:

```sh
python scripts/select_model.py examples/catalogue.json
```

The example selects `standard-code`: the lower-ranked candidate lacks debugging capability, and the unavailable candidate is excluded. Tests cover mismatched input/output cost metrics, unknown evidence, duplicate IDs, and invalid catalogue roots. Invalid JSON or malformed catalogue data exits with a named command-line validation error and no selection.

Created by ALTA VISTA360, S.L.U. (`kanibal-studio`).

- [Altavista360](https://altavista360.com/)
- [Altavista Conseil](https://altavista-conseil.com/)
- [Kanibal Studio](https://infos.kanibal-studio.com/)

Licensed under the [MIT License](LICENSE).
