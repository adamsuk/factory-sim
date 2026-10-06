# Factory sim viewer

Reads `src/` from this repo. It does not copy `part.py`, `belt.py`, `worker.py`, `const.py` or `sim.py`.

`runner.py` loads those files from `../src`. `sim.py` still autoruns on a normal import, so the runner drops that trailing block in memory and leaves the file alone.

The React component fetches the same `src/*.py` files, plus this runner, from the repo. The site does not vendor the sim.

## Site

Copy only `viz/src` into `components/sandbox/factorySim`. The component loads:

`https://raw.githubusercontent.com/adamsuk/factory-sim/<ref>/src/<module>.py`

`<ref>` defaults to `main`. Point it at another branch only while this viewer is unmerged.
