# Contributing to Momentum

Momentum is currently maintained as a proprietary project. Contributions are
accepted only when explicitly requested by the maintainer.

Before submitting a change:

1. Read the repository license and third-party notice requirements.
2. Keep secrets, personal data, local databases, logs, and generated builds
   out of commits. The one exception is `momentum/database/momentum.db`,
   the shipped seed database that fresh installs load tracks and world data
   from. Rebuild it with `python -m momentum.seed.build` (the build is
   deterministic, so the same source gives the same file) and commit it only
   for intentional seed changes, never with local save or race data.
3. Run `python -m pytest` from the repository root.
4. Describe user-visible changes and any new asset or dependency licenses.

By submitting a contribution, you confirm that you have the right to submit
it and grant the copyright holder permission to use it in Momentum releases.
The maintainer may require a separate contribution agreement for substantial
or commercial contributions.