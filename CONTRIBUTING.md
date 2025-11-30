# Contributing Guidelines

## Language and Spelling

- Use Irish English spelling throughout the project documentation (aligns with common UK/Irish conventions).
- Maintain the following preferred spellings (non-exhaustive):
  - `optimisation` (not `optimization`)
  - `optimise` (not `optimize`)
  - `customisation` / `customised` (not `customization` / `customized`)
  - `behaviour` / `behavioural` (not `behavior` / `behavioral`)
  - `analyse` / `analysed` / `analysing` (not `analyze` / `analyzed` / `analyzing`)
  - `colour` / `colours` (not `color` / `colors`)
  - `organise` / `organised` (not `organize` / `organized`)
  - `prioritise` / `prioritised` (not `prioritize` / `prioritized`)
  - `centre` / `centred` (not `center` / `centered`)
  - `modelling` / `modeller` (not `modeling` / `modeler`)
  - `localisation` (not `localization`)

Rationale

- Consistent spelling improves maintainability and readability for the intended audience.

Automation

- A helper script is provided at `tools/convert_to_english.py` to perform a conservative conversion of documentation files.
- The script is conservative: it skips code fences and inline code spans to avoid changing code identifiers or tokens.

Never Use American English in Docs

- Documentation PRs should follow this guideline. Avoid using American spelling in new or updated docs; if present, replace before merging.
