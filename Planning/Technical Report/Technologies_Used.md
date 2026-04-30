# Technologies Used in Momentum

This document lists the technologies used in the project with rationale, advantages, disadvantages, and current usage status.

Source evidence used:

- [Momentum/Python/requirements.txt](Momentum/Python/requirements.txt)
- [Momentum/Python/simulation.py](Momentum/Python/simulation.py)
- [Momentum/Python/GUI/launcher.py](Momentum/Python/GUI/launcher.py)
- [Momentum/Python/config.py](Momentum/Python/config.py)
- [Momentum/Python/RaceLogic/closure_solver.py](Momentum/Python/RaceLogic/closure_solver.py)
- [Momentum/Python/tools/team_name_generator.py](Momentum/Python/tools/team_name_generator.py)
- [Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md](Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md)
- https://www.statology.org/the-concise-guide-to-weibull-distribution/
- https://www.cs.umd.edu/users/oleary/reprints/j51.pdf

## Core Runtime Stack

| Technology               | Role in Project                                                         | Reason for Use                                                   | Advantages                                              | Disadvantages                                                              | Status | Word Source Tag        |
| ------------------------ | ----------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------- | ------ | ---------------------- |
| Python 3.13              | Main programming language for backend, simulation, scripts, and tooling | Fast iteration for research-heavy simulation and desktop tooling | Very productive, huge ecosystem, readable code          | Slower than compiled languages for heavy compute hotspots                  | Active | `PythonDocs2026`     |
| FastAPI                  | REST API framework                                                      | Typed API contracts and rapid endpoint development               | Automatic validation/docs, clean async support          | Ecosystem smaller than older frameworks, can be overkill for tiny APIs     | Active | `FastAPIDocs2026`    |
| Uvicorn                  | ASGI server for FastAPI                                                 | Lightweight local server for development and testing             | Fast startup, simple deployment                         | Production setups still need process management and reverse proxy strategy | Active | `UvicornDocs2026`    |
| Pydantic                 | Request/response model validation                                       | Strong schema validation for API payloads                        | Reduces invalid input bugs, clear typed models          | Validation overhead and migration friction across versions                 | Active | `PydanticDocs2026`   |
| SQLite (builtin sqlite3) | Local persistence layer                                                 | Single-file database for local desktop-friendly distribution     | Zero-admin, portable, simple backups                    | Limited write concurrency and less scalability than server DBs             | Active | `SQLiteDocs2026`     |
| PyQt6                    | Desktop GUI framework                                                   | Native desktop UI for race visualisation and management screens  | Good desktop performance and widget set, mature toolkit | Larger packaging footprint, cross-platform styling quirks                  | Active | `PyQt62026`          |
| NumPy                    | Numerical operations in race logic                                      | Efficient vector/numeric processing for simulation operations    | Fast array operations, scientific ecosystem standard    | Debugging vectorised logic can be harder for newcomers                     | Active | `NumPyDocs2026`      |
| SciPy                    | Optimisation/integration in solver components                           | Needed for nonlinear solver and related maths utilities          | Strong scientific algorithms and solvers                | Heavy dependency, startup/install overhead                                 | Active | `SciPyDocs2026`      |
| Matplotlib               | Plotting and visual telemetry                                           | Post-race charts and visual trend outputs                        | Reliable plotting, well understood                      | Styling defaults are basic, interactive UX can feel dated                  | Active | `MatplotlibDocs2026` |

## Supporting Libraries

| Technology    | Role in Project                    | Reason for Use                                             | Advantages                                           | Disadvantages                                                   | Status                | Word Source Tag       |
| ------------- | ---------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------- | --------------------- | --------------------- |
| Faker         | Synthetic names/data generation    | Seed realistic teams, drivers, staff, and naming utilities | Quick realistic fake data generation, locale support | Can still generate repetitive outputs without constraints       | Active                | `FakerDocs2026`     |
| python-dotenv | Environment configuration loading  | Keep environment-specific settings out of source           | Simple .env workflow, improves portability           | Easy to accumulate stale/undocumented env keys                  | Active                | `DotenvDocs2026`    |
| Pillow (PIL)  | Image generation tooling           | Asset/helper scripts for placeholder sprites and tiles     | Simple API for 2D image generation                   | Not intended for advanced realtime graphics                     | Active (tool scripts) | `PillowDocs2026`    |
| unidecode     | Text normalisation/transliteration | Normalise generated names across locales                   | Improves compatibility for ASCII-safe output         | Transliteration can lose language-specific nuance               | Active                | `UnidecodePyPI2026` |
| Shapely       | Geometry operations                | Track and geometry-related operations                      | Powerful geometry primitives                         | Additional binary dependency and version compatibility concerns | Declared/planned      | `ShapelyDocs2026`   |

## Data and ML Dependencies Declared

| Technology      | Role in Project                | Reason for Use                                   | Advantages                                         | Disadvantages                                                   | Status           | Word Source Tag     |
| --------------- | ------------------------------ | ------------------------------------------------ | -------------------------------------------------- | --------------------------------------------------------------- | ---------------- | ------------------- |
| pandas          | Data analysis/export workflows | Tabular telemetry analysis and reporting support | Excellent data-frame tooling, CSV/report workflows | Can be memory-heavy and slower than pure NumPy for simple tasks | Declared/planned | `PandasDocs2026`  |
| torch (PyTorch) | Experimental ML capability     | Future behaviour modelling and experimentation   | Strong ML ecosystem and flexibility                | Large dependency footprint and GPU/CPU environment complexity   | Declared/planned | `PyTorchDocs2026` |

## Testing and Quality Tooling

| Technology | Role in Project              | Reason for Use                            | Advantages                             | Disadvantages                                                  | Status               | Word Source Tag     |
| ---------- | ---------------------------- | ----------------------------------------- | -------------------------------------- | -------------------------------------------------------------- | -------------------- | ------------------- |
| pytest     | Unit/integration test runner | Simple, scalable test authoring           | Fixtures, markers, readable tests      | Plugin/config sprawl possible on large suites                  | Active               | `PytestDocs2026`  |
| pytest-cov | Coverage reporting           | Quantify tested code paths                | Straightforward coverage metrics       | Coverage percentage can be gamed without meaningful assertions | Active               | `PytestCov2026`   |
| black      | Formatting                   | Enforce consistent code formatting        | Removes style debates, fast formatting | Opinionated formatting choices                                 | Active               | `BlackDocs2026`   |
| flake8     | Linting                      | Catch style and simple quality issues     | Lightweight and familiar               | Needs configuration to avoid noisy warnings                    | Active               | `Flake8Docs2026`  |
| mypy       | Static type checking         | Improve correctness in typed Python code  | Catches interface/type errors early    | Requires disciplined annotations and stubs                     | Active               | `MypyDocs2026`    |
| hypothesis | Property-based testing       | Generate extensive test cases from specifications | Finds edge cases automatically, improves coverage | Requires rethinking test design around properties           | Active               | `HypothesisDocs2026` |
| ipython    | Developer shell tooling      | Interactive debugging and experimentation | Fast exploratory workflow              | Not part of runtime deliverable                                | Active (development) | `IPythonDocs2026` |

## Mathematical Formulae and Method References

This section links report-citable mathematics and optimisation methods to concrete implementation areas. It is intended to support Section 1.3 (Technology) and mathematical justification sections.

| Mathematical Component | Where Used in Project | Why It Is Included | Referenceable Source |
| ---------------------- | --------------------- | ------------------ | -------------------- |
| Weibull reliability and incremental hazard | Solo failure hazard and wear-out behaviour in realtime simulation logic, documented in [Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md](Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md) Section 6b | Models non-constant failure rates and realistic wear-out dynamics instead of flat per-lap failure chance | Internal: [Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md](Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md). External explainer: https://www.statology.org/the-concise-guide-to-weibull-distribution/ |
| Logistic probability mapping | Overtake success and incident-risk shaping in overtaking logic, documented in [Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md](Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md) Section 5 | Provides bounded probabilities and diminishing returns compared with linear probability scoring | Internal: [Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md](Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md) |
| Derivative-free optimisation (Powell primary, Nelder-Mead fallback) | Closure solver optimisation stages in [Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md](Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md) Section 11 | Improves robustness for nonlinear closure under bounded parameters without requiring derivatives | Internal: [Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md](Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md). External reference provided: https://www.cs.umd.edu/users/oleary/reprints/j51.pdf |
| Monte Carlo sampling for stochastic race outcomes | Stochastic race modelling and uncertainty propagation, documented in [Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md](Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md) and supported by bibliography tag `MetropolisUlam1949` | Captures uncertainty in incidents, performance variability, and race outcome distributions | Internal: [Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md](Momentum/Python/docs/MATHEMATICS_AND_FUNCTION_SOURCES.md). Primary theory reference: Metropolis and Ulam (1949) |

Suggested report wording for citation scope:

- Use the internal maths document as implementation evidence.
- Use external links for conceptual background and method context.
- Keep foundational academic sources (for example Metropolis and Ulam, 1949) as primary references where possible.

## Notes for Report Usage

- In Section 1.3 Technology, cite the core runtime stack first.
- In Implementation, reference only technologies actually wired into current code paths.
- In Future Development, include declared/planned technologies (for example torch, pandas, shapely) and explicitly label them as planned or partially integrated.
- Keep the bibliography aligned with [Planning/Technical Report/word_sources_harvard.xml](Planning/Technical%20Report/word_sources_harvard.xml).
- The `Word Source Tag` column maps directly to `Tag` values in [Planning/Technical Report/word_sources_harvard.xml](Planning/Technical%20Report/word_sources_harvard.xml).
