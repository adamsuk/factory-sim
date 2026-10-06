"""Run factory-sim without modifying its modules.

The files in this directory are verbatim copies of factory-sim/src.
This runner loads them in memory, overrides const globals, and strips the
autorun at the bottom of sim.py before exec. Nothing on disk is rewritten.
"""

import io
import random
import sys
import types

AUTORUN = "\nenv = simpy.Environment()"


def _module(name, source):
    if name == "sim":
        cut = source.find(AUTORUN)
        if cut == -1:
            raise RuntimeError("sim.py autorun marker missing; refusing to import it")
        source = source[:cut]
    module = types.ModuleType(name)
    module.__dict__["__name__"] = name
    exec(compile(source, f"{name}.py", "exec"), module.__dict__)
    sys.modules[name] = module
    return module


def run(sources, inputs):
    """Return one frame per tick. sources maps filename -> text."""
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

    return {
        "frames": frames,
        "inputs": overrides,
        "log": sink.getvalue(),
    }
