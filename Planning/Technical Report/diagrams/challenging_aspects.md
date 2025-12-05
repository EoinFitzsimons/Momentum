# Challenging Aspects, Options and Resolutions

## 1) Visual race loop

- Challenge: Monte Carlo finished instantly and gave no live GUI feedback or on the fly control
- Resolution: Implemented a frame by frame race loop at about 30 FPS with per tick decisions and live GUI updates
- Alternatives: Artificial delays on Monte Carlo rejected, lap or sector stepping rejected
- Next: Add sim speed control, telemetry sampling and readable tick logs

## 2) Synthetic data without IP risk

- Challenge: Need many drivers, teams and circuits without licensing or copyright issues
- Resolution: Procedural generation using Faker across locales and storing circuits in JSON and SQLite
- Alternatives: Real world datasets rejected for licence risk, single locale names rejected for low authenticity
- Next: Add a validation script to catch real name collisions and apply locale weighting per discipline

## 3) Extensible base engine

- Challenge: One core engine that supports discipline specific rules without duplicated code
- Resolution: BaseDisciplineEngine with a DisciplineContext. Derived engines override weightings and event hooks
- Alternatives: Per discipline bespoke engines rejected, single monolith with many if and else rejected
- Next: Publish an extension checklist, add contract tests and include a small exemplar discipline

Related diagrams and files

- IA sitemap and navigation map for screens and flows
- Wireframes for the race, setup and results screens
- Activity and sequence diagrams for the race tick loop and session flow
- Architecture diagram and CRUD matrix for engine and data responsibilities
- Data files such as circuits_database JSON and the Faker configuration in config
