# Factory sim viewer

Import this repo. Do not copy `src/` or the component into the site.

```bash
npm install github:adamsuk/factory-sim#v0.2.1
```

```tsx
import FactorySim from "factory-sim-viz";
```

The package reads `src/*.py` and `viz/runner.py` from the installed ref at runtime. `src/` is not modified. `sim.py` still autoruns on a normal import, so the runner removes that trailing block in memory.

Next.js needs `transpilePackages: ["factory-sim-viz"]`.

## Release test

Publishing a GitHub release runs `.github/workflows/pages.yml` and deploys a Pages app that loads `src/` from that tag. Run it by hand with the Actions `workflow_dispatch` event before the first tag. Pages must be set to deploy from GitHub Actions.
