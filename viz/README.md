# Factory sim viewer

A browser viewer for [factory-sim](https://github.com/adamsuk/factory-sim). It does not change `src/`.

`viz/engine/part.py`, `belt.py`, `worker.py`, `const.py` and `sim.py` are verbatim copies of `src/`. `runner.py` loads those strings, overrides the `const` globals, and cuts the `env.run(...)` autorun off in memory before exec. The copies on disk still contain the autorun.

The React component runs that runner in Pyodide, so the belt you see is the SimPy loop, not a port. Inputs (ticks, belt size, assemble delay, seed, part types, the part a worker must collect, worker sides) are passed in and the run is replayed.

## Use it on sradams.co.uk

Copy into the site repo:

- `viz/src/FactorySim.tsx` -> `components/sandbox/factorySim/FactorySim.tsx`
- `viz/src/engineSources.ts` -> `components/sandbox/factorySim/engineSources.ts`
- `viz/src/index.ts` -> `components/sandbox/factorySim/index.ts`

Register it in `components/sandbox/index.tsx`:

```tsx
import FactorySim from './factorySim';

const sandboxes = [
  { title: 'Factory sim', slug: 'factory-sim', component: FactorySim },
  // existing entries
];
```

No extra npm dependency. Pyodide and SimPy load from a CDN the first time the sandbox opens.

The site PR `factory-sim-sandbox` does this copy. If the engine files here change, regenerate `engineSources.ts` from `viz/engine` and copy it again.
