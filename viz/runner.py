"""Run factory-sim by importing src/. Does not copy or edit those modules.

sim.py autoruns on import, so it is read from disk and the trailing
`env = simpy.Environment()` block is removed only in memory.
"""

import io
import random
import sys
import types
from pathlib import Path

AUTORUN = "\nenv = simpy.Environment()"
SRC = Path(__file__).resolve().parents[1] / "src"
MODULES = ("part.py", "belt.py", "worker.py", "const.py", "sim.py")


def sources_from_src(src_dir=SRC):
    src_dir = Path(src_dir)
    missing = [name for name in MODULES if not (src_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"{src_dir} is missing {', '.join(missing)}")
    return {name: (src_dir / name).read_text() for name in MODULES}


def _module(name, source):
    if name == "sim":
        cut = source.find(AUTORUN)
        if cut == -1:
            raise RuntimeError("src/sim.py autorun marker missing; refusing to import it")
        source = source[:cut]
    module = types.ModuleType(name)
    module.__dict__["__name__"] = name
    exec(compile(source, f"src/{name}.py", "exec"), module.__dict__)
    sys.modules[name] = module
    return module


def run(sources, inputs):
    """sources is the text of src/part.py, belt.py, worker.py, const.py, sim.py."""
    for name in ("part", "const", "belt", "worker", "sim"):
        sys.modules.pop(name, None)

    part_types = [p.strip() for p in inputs.get("part_types", ["A", "B"]) if str(p).strip()]
    complete_part = [p.strip() for p in inputs.get("complete_part", ["A", "B"]) if str(p).strip()]
    worker_positions = inputs.get("worker_positions") or ["top", "bottom"]
    overrides = {
        "sim_time": int(inputs.get("sim_time", 40)),
        "belt_size": int(inputs.get("belt_size", 5)),
        "complete_delay": int(inputs.get("complete_delay", 4)),
        "part_types": part_types,
        "worker_positions": list(worker_positions),
        "complete_part": complete_part,
    }
    if not part_types or not complete_part or not worker_positions:
        raise ValueError("part types, complete part and worker sides are required")
    if overrides["belt_size"] < 1 or overrides["sim_time"] < 1:
        raise ValueError("belt size and ticks must be at least 1")

    random.seed(int(inputs.get("seed", 1)))
    _module("part", sources["part.py"])
    const = _module("const", sources["const.py"])
    for key, value in overrides.items():
        setattr(const, key, value)
    _module("belt", sources["belt.py"])
    _module("worker", sources["worker.py"])
    sim = _module("sim", sources["sim.py"])

    import simpy

    belt_ref = {}
    workers = []
    stats = {"total": 0, "complete": 0, "waste": 0}
    Belt = sys.modules["belt"].Belt
    Worker = sys.modules["worker"].Worker
    orig_belt_init = Belt.__init__
    orig_worker_init = Worker.__init__
    orig_add = Belt.add

    def belt_init(self, size=4):
        orig_belt_init(self, size)
        belt_ref["belt"] = self

    def worker_init(self, *args, **kwargs):
        orig_worker_init(self, *args, **kwargs)
        workers.append(self)

    def add(self, item):
        last = orig_add(self, item)
        if item.peek() is not None:
            stats["total"] += 1
        if last.complete:
            stats["complete"] += 1
        elif last.peek() is not None:
            stats["waste"] += 1
        return last

    Belt.__init__ = belt_init
    Worker.__init__ = worker_init
    Belt.add = add
    sink = io.StringIO()
    previous = sys.stdout
    sys.stdout = sink
    try:
        env = simpy.Environment()
        env.process(sim.factory(env))
        frames = []
        limit = overrides["sim_time"]
        while env.peek() < limit:
            env.step()
            belt = belt_ref["belt"]
            frames.append({
                "t": int(env.now),
                "belt": [slot.peek() for slot in belt.belt],
                "complete": [bool(slot.complete) for slot in belt.belt],
                "hands": [{
                    "side": worker.side,
                    "pos": worker.pos,
                    "hand": [item.peek() for item in worker.hand],
                    "busyUntil": worker.complete_time,
                } for worker in workers],
                "total": stats["total"],
                "finished": stats["complete"],
                "waste": stats["waste"],
            })
    finally:
        sys.stdout = previous
        Belt.__init__ = orig_belt_init
        Worker.__init__ = orig_worker_init
        Belt.add = orig_add

    return {"frames": frames, "inputs": overrides, "log": sink.getvalue()}


def run_from_src(inputs, src_dir=SRC):
    return run(sources_from_src(src_dir), inputs)
