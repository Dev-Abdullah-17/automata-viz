# AutomataViz — DFA/NFA Simulator & Converter

An interactive tool for building finite automata, running strings through them step by step, and converting an NFA into an equivalent DFA — with every conversion step shown, not just the final result. Built to make the theory-of-computation concepts I teach visible rather than abstract.

**Live demo:**https://automata-viz-tau.vercel.app/

## What it does

- **Simulate a DFA** on an input string and see whether it's accepted or rejected, one transition at a time.
- **Simulate an NFA**, including ε-transitions, tracking the full set of active states at each step.
- **Convert an NFA to a DFA** via subset construction, with a written trace of every generated state (`ε-closure(...) = {...}`) so the algorithm is legible, not a black box.
- **Load preset examples** (e.g. "strings ending in 01", "even number of 0s") to explore without building a machine from scratch.

## The problem it solves

Finite automata are usually taught on a whiteboard: you draw states and arrows, trace a string by hand, and the NFA→DFA subset construction is a tedious table you fill in manually and hope you didn't miss a state. That's exactly where students lose the thread. AutomataViz makes the machine executable — you define it, feed it a string, and watch the active states move — and it exposes the subset-construction *steps*, which is the part that's hard to follow when it's just a final transition table.

## How it works

```
Browser (canvas UI)
    │  define states / alphabet / transitions / input
    ▼
FastAPI backend  (main.py)
    ├── POST /simulate/dfa      → dfa.py    step-by-step DFA run
    ├── POST /simulate/nfa      → nfa.py    NFA run with ε-closure tracking
    ├── POST /convert/nfa-to-dfa→ converter.py  subset construction + step trace
    └── GET  /examples          preset DFAs / NFAs
    ▼
JSON trace (states visited, accept/reject, construction steps)
    ▼
Canvas frontend animates the run and renders the result
```

The core logic is plain Python — no automata library — so the DFA/NFA definitions and the subset-construction algorithm are all readable in `dfa.py`, `nfa.py`, and `converter.py`. `converter.py` returns the DFA definition *and* a `construction_steps` list describing how each DFA state was derived from an NFA state set, which is what the UI uses to explain the conversion.

## Tech stack

| Layer | Technology |
|---|---|
| Backend / API | FastAPI + Uvicorn |
| Request validation | Pydantic |
| Automata logic | Pure Python (no external automata library) |
| Frontend | Vanilla HTML/JS + Canvas (no framework) |
| Deployment | Railway |

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000` — the backend serves the frontend at the root route.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET`  | `/` | Serves the frontend |
| `POST` | `/simulate/dfa` | Run a string through a DFA |
| `POST` | `/simulate/nfa` | Run a string through an NFA (ε-transitions supported) |
| `POST` | `/convert/nfa-to-dfa` | Subset construction, returns DFA + step trace |
| `GET`  | `/examples` | Preset DFA/NFA definitions |

## Limitations / roadmap

- No DFA minimization yet (subset construction can produce redundant states).
- No regular-expression → NFA (Thompson construction) entry point.
- Definitions are entered per session; there's no save/load of custom machines.
- The repository currently has some duplication to clean up: the automata modules exist both at the project root and under `engine/`, and `engine/__init__.py.txt` should be a real `__init__.py`. `main.py` imports the root-level copies, so `engine/` can either be removed or made the single source of truth.
