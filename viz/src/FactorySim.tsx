import React, { useEffect, useMemo, useRef, useState } from "react";
import { engineSources } from "./engineSources";

type Hand = {
  side: string;
  pos: number;
  hand: Array<string | null>;
  busyUntil: number | null;
};

type Frame = {
  t: number;
  belt: Array<string | null>;
  complete: boolean[];
  hands: Hand[];
  total: number;
  finished: number;
  waste: number;
};

type RunResult = {
  frames: Frame[];
  log: string;
};

type Inputs = {
  sim_time: number;
  belt_size: number;
  complete_delay: number;
  seed: number;
  part_types: string[];
  complete_part: string[];
  worker_positions: string[];
};

const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js";

const PART_COLOURS: Record<string, string> = {
  A: "bg-sky-500 text-white",
  B: "bg-amber-500 text-white",
  P: "bg-emerald-500 text-white",
};

function partClass(type: string | null, complete: boolean) {
  if (complete) return PART_COLOURS.P;
  if (!type) return "border border-dashed border-gray-300 text-gray-400 dark:border-gray-600";
  return PART_COLOURS[type] || "bg-violet-500 text-white";
}

function loadPyodideScript(): Promise<(options: { indexURL: string }) => Promise<Pyodide>> {
  const existing = (window as unknown as { loadPyodide?: (options: { indexURL: string }) => Promise<Pyodide> }).loadPyodide;
  if (existing) return Promise.resolve(existing);
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = PYODIDE;
    script.async = true;
    script.onload = () => {
      const loader = (window as unknown as { loadPyodide?: (options: { indexURL: string }) => Promise<Pyodide> }).loadPyodide;
      if (!loader) reject(new Error("Pyodide did not register"));
      else resolve(loader);
    };
    script.onerror = () => reject(new Error("Could not load Pyodide"));
    document.body.appendChild(script);
  });
}

type Pyodide = {
  loadPackage: (name: string) => Promise<void>;
  runPythonAsync: (code: string) => Promise<void>;
  globals: {
    set: (name: string, value: unknown) => void;
    get: (name: string) => { toJs: (options: { dict_converter: typeof Object.fromEntries }) => RunResult };
  };
};

let pyodidePromise: Promise<Pyodide> | null = null;

function getPyodide() {
  if (!pyodidePromise) {
    pyodidePromise = (async () => {
      const loadPyodide = await loadPyodideScript();
      const pyodide = await loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/" });
      await pyodide.loadPackage("micropip");
      await pyodide.runPythonAsync("import micropip\nawait micropip.install('simpy')");
      return pyodide;
    })();
  }
  return pyodidePromise;
}

async function runSim(inputs: Inputs): Promise<RunResult> {
  const pyodide = await getPyodide();
  pyodide.globals.set("sources", engineSources);
  pyodide.globals.set("inputs", inputs);
  const payload = await pyodide.runPythonAsync(`
import json
ns = {}
exec(sources["runner.py"], ns)
raw = inputs.to_py() if hasattr(inputs, "to_py") else dict(inputs)
files = {key: sources[key] for key in sources.keys() if key != "runner.py"}
result = ns["run"](files, raw)
json.dumps(result)
`);
  return JSON.parse(String(payload)) as RunResult;
}

function WorkerRow({ side, frame }: { side: string; frame: Frame }) {
  const slots = frame.belt.map((_, pos) => frame.hands.find((hand) => hand.side === side && hand.pos === pos));
  return (
    <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${frame.belt.length}, minmax(0, 1fr))` }}>
      {slots.map((worker, pos) => {
        const busy = worker?.busyUntil != null && frame.t < worker.busyUntil;
        const holding = worker?.hand.filter(Boolean).join(" + ") || "empty";
        return (
          <div key={`${side}-${pos}`} className={`rounded-md px-2 py-2 text-center text-xs ${busy ? "bg-emerald-100 dark:bg-emerald-950" : "bg-gray-100 dark:bg-gray-800"}`}>
            <div className="font-medium uppercase tracking-wide text-gray-500">{side}</div>
            <div className="mt-1 truncate text-gray-900 dark:text-gray-100">{holding}</div>
            <div className="text-[10px] text-gray-500">{busy ? `assembling until ${worker?.busyUntil}` : "watching"}</div>
          </div>
        );
      })}
    </div>
  );
}

export default function FactorySim() {
  const [ticks, setTicks] = useState(40);
  const [beltSize, setBeltSize] = useState(5);
  const [delay, setDelay] = useState(4);
  const [seed, setSeed] = useState(1);
  const [partTypes, setPartTypes] = useState("A, B");
  const [completePart, setCompletePart] = useState("A, B");
  const [top, setTop] = useState(true);
  const [bottom, setBottom] = useState(true);
  const [result, setResult] = useState<RunResult | null>(null);
  const [cursor, setCursor] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [status, setStatus] = useState("Loading the sim");
  const [error, setError] = useState("");
  const [showLog, setShowLog] = useState(false);
  const runId = useRef(0);

  const inputs = useMemo<Inputs>(() => ({
    sim_time: ticks,
    belt_size: beltSize,
    complete_delay: delay,
    seed,
    part_types: partTypes.split(",").map((part) => part.trim()).filter(Boolean),
    complete_part: completePart.split(",").map((part) => part.trim()).filter(Boolean),
    worker_positions: [top ? "top" : "", bottom ? "bottom" : ""].filter(Boolean),
  }), [ticks, beltSize, delay, seed, partTypes, completePart, top, bottom]);

  useEffect(() => {
    const id = runId.current + 1;
    runId.current = id;
    setStatus("Running factory-sim");
    setError("");
    runSim(inputs).then((next) => {
      if (runId.current !== id) return;
      setResult(next);
      setCursor(0);
      setPlaying(true);
      setStatus(`Ran ${next.frames.length} ticks in the original modules`);
    }).catch((reason: unknown) => {
      if (runId.current !== id) return;
      setError(reason instanceof Error ? reason.message : "Sim failed");
      setStatus("Sim failed");
    });
  }, [inputs]);

  useEffect(() => {
    if (!playing || !result?.frames.length) return undefined;
    const timer = window.setInterval(() => {
      setCursor((current) => (current + 1) % result.frames.length);
    }, 450);
    return () => window.clearInterval(timer);
  }, [playing, result]);

  const frame = result?.frames[cursor];

  return (
    <div className="mx-auto w-full max-w-3xl rounded-lg bg-gray-50 p-4 shadow-sm dark:bg-gray-900">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Factory sim</h2>
          <p className="text-sm text-gray-500">{status}. Src modules are unchanged; inputs override const in memory.</p>
        </div>
        <div className="flex gap-2">
          <button type="button" className="rounded-full bg-gray-900 px-3 py-1 text-sm text-white dark:bg-white dark:text-gray-900" onClick={() => setPlaying((value) => !value)}>
            {playing ? "Pause" : "Play"}
          </button>
          <button type="button" className="rounded-full bg-gray-200 px-3 py-1 text-sm dark:bg-gray-800" onClick={() => setCursor((value) => Math.max(0, value - 1))}>Step back</button>
          <button type="button" className="rounded-full bg-gray-200 px-3 py-1 text-sm dark:bg-gray-800" onClick={() => result && setCursor((value) => Math.min(result.frames.length - 1, value + 1))}>Step</button>
        </div>
      </div>

      <div className="mb-4 grid gap-3 sm:grid-cols-4">
        <label className="text-xs text-gray-500">Ticks
          <input className="mt-1 w-full rounded border border-gray-300 bg-white px-2 py-1 text-sm dark:border-gray-700 dark:bg-gray-950" type="number" min={5} max={200} value={ticks} onChange={(event) => setTicks(Number(event.target.value))} />
        </label>
        <label className="text-xs text-gray-500">Belt size
          <input className="mt-1 w-full rounded border border-gray-300 bg-white px-2 py-1 text-sm dark:border-gray-700 dark:bg-gray-950" type="number" min={2} max={10} value={beltSize} onChange={(event) => setBeltSize(Number(event.target.value))} />
        </label>
        <label className="text-xs text-gray-500">Assemble delay
          <input className="mt-1 w-full rounded border border-gray-300 bg-white px-2 py-1 text-sm dark:border-gray-700 dark:bg-gray-950" type="number" min={1} max={20} value={delay} onChange={(event) => setDelay(Number(event.target.value))} />
        </label>
        <label className="text-xs text-gray-500">Seed
          <input className="mt-1 w-full rounded border border-gray-300 bg-white px-2 py-1 text-sm dark:border-gray-700 dark:bg-gray-950" type="number" value={seed} onChange={(event) => setSeed(Number(event.target.value))} />
        </label>
        <label className="text-xs text-gray-500 sm:col-span-2">Part types fed onto the belt
          <input className="mt-1 w-full rounded border border-gray-300 bg-white px-2 py-1 text-sm dark:border-gray-700 dark:bg-gray-950" value={partTypes} onChange={(event) => setPartTypes(event.target.value)} />
        </label>
        <label className="text-xs text-gray-500 sm:col-span-2">Parts a worker must collect
          <input className="mt-1 w-full rounded border border-gray-300 bg-white px-2 py-1 text-sm dark:border-gray-700 dark:bg-gray-950" value={completePart} onChange={(event) => setCompletePart(event.target.value)} />
        </label>
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={top} onChange={(event) => setTop(event.target.checked)} /> Top workers</label>
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={bottom} onChange={(event) => setBottom(event.target.checked)} /> Bottom workers</label>
      </div>

      {error && <p className="mb-3 text-sm text-red-600">{error}</p>}

      {frame && (
        <div className="space-y-2">
          <div className="flex flex-wrap gap-4 text-sm">
            <span>Tick {frame.t}</span>
            <span>Fed {frame.total}</span>
            <span>Finished {frame.finished}</span>
            <span>Waste {frame.waste}</span>
          </div>
          {top && <WorkerRow side="top" frame={frame} />}
          <div className="grid gap-2 rounded-md bg-gray-200 p-2 dark:bg-gray-800" style={{ gridTemplateColumns: `repeat(${frame.belt.length}, minmax(0, 1fr))` }}>
            {frame.belt.map((part, index) => (
              <div key={`slot-${index}`} className={`flex h-16 items-center justify-center rounded-md text-sm font-semibold ${partClass(part, frame.complete[index])}`}>
                {frame.complete[index] ? "P" : part || "·"}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-[10px] uppercase tracking-wide text-gray-500">
            <span>Infeed</span>
            <span>Outfeed</span>
          </div>
          {bottom && <WorkerRow side="bottom" frame={frame} />}
          <input className="w-full" type="range" min={0} max={Math.max(0, (result?.frames.length || 1) - 1)} value={cursor} onChange={(event) => { setPlaying(false); setCursor(Number(event.target.value)); }} />
        </div>
      )}

      <button type="button" className="mt-3 text-xs text-gray-500 underline" onClick={() => setShowLog((value) => !value)}>
        {showLog ? "Hide" : "Show"} original sim log
      </button>
      {showLog && <pre className="mt-2 max-h-48 overflow-auto rounded bg-gray-900 p-3 text-[11px] text-gray-100">{result?.log || "No log yet"}</pre>}
    </div>
  );
}
