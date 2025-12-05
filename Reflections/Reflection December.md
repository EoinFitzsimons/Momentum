# December 2025 Reflection

| Student Name   | Eoin Andrew Fitzsimons                      |
| -------------- | ------------------------------------------- |
| Student Number | X23151374                                   |
| Course         | BSc (Hons) Computing - Software Development |

Month: December 2025

What?

- Built the real-time agent engine and connected it to the GUI.
- Fixed a set of code warnings and cleaned up some function signatures.
- Ran tests (quick checks and longer validation runs).

So What?

- The project now simulates live racing: cars move continuously and agents make per-frame decisions (attack/defend/manage/cruise).
-- This change gives visible, interactive behaviour for demos, but some core docs still describe the legacy Monte Carlo approach.
- We also found balance issues: too many DNFs in long races that need tuning.

Now What?

- Rewrite the technical report and proposal to describe the agent-based approach.
- Tune incident and tire/fuel parameters to reduce DNFs (<30% target).
- Run GUI end-to-end tests and import track data for the midpoint demo.
