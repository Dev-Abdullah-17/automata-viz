from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional

from dfa import DFADefinition, simulate_dfa
from nfa import NFADefinition, simulate_nfa
from converter import nfa_to_dfa

app = FastAPI(title="AutomataViz", description="DFA/NFA Simulator & Converter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")


# ── Request Models ──────────────────────────────────────────────────────────

class DFARequest(BaseModel):
    states: List[str]
    alphabet: List[str]
    transitions: Dict[str, Dict[str, str]]
    start_state: str
    accept_states: List[str]
    input_string: str


class NFARequest(BaseModel):
    states: List[str]
    alphabet: List[str]
    transitions: Dict[str, Dict[str, List[str]]]
    start_state: str
    accept_states: List[str]
    input_string: str


class NFAConvertRequest(BaseModel):
    states: List[str]
    alphabet: List[str]
    transitions: Dict[str, Dict[str, List[str]]]
    start_state: str
    accept_states: List[str]


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse("index.html")


@app.post("/simulate/dfa")
def simulate_dfa_route(req: DFARequest):
    dfa = DFADefinition(
        states=req.states,
        alphabet=req.alphabet,
        transitions=req.transitions,
        start_state=req.start_state,
        accept_states=req.accept_states
    )
    return simulate_dfa(dfa, req.input_string)


@app.post("/simulate/nfa")
def simulate_nfa_route(req: NFARequest):
    nfa = NFADefinition(
        states=req.states,
        alphabet=req.alphabet,
        transitions=req.transitions,
        start_state=req.start_state,
        accept_states=req.accept_states
    )
    return simulate_nfa(nfa, req.input_string)


@app.post("/convert/nfa-to-dfa")
def convert_nfa_to_dfa_route(req: NFAConvertRequest):
    nfa = NFADefinition(
        states=req.states,
        alphabet=req.alphabet,
        transitions=req.transitions,
        start_state=req.start_state,
        accept_states=req.accept_states
    )
    return nfa_to_dfa(nfa)


# ── Preset Examples ─────────────────────────────────────────────────────────

@app.get("/examples")
def get_examples():
    return {
        "dfa_examples": [
            {
                "name": "Strings ending in '01' over {0,1}",
                "states": ["q0", "q1", "q2"],
                "alphabet": ["0", "1"],
                "transitions": {
                    "q0": {"0": "q1", "1": "q0"},
                    "q1": {"0": "q1", "1": "q2"},
                    "q2": {"0": "q1", "1": "q0"}
                },
                "start_state": "q0",
                "accept_states": ["q2"]
            },
            {
                "name": "Strings with even number of 0s",
                "states": ["q0", "q1"],
                "alphabet": ["0", "1"],
                "transitions": {
                    "q0": {"0": "q1", "1": "q0"},
                    "q1": {"0": "q0", "1": "q1"}
                },
                "start_state": "q0",
                "accept_states": ["q0"]
            }
        ],
        "nfa_examples": [
            {
                "name": "Strings ending in 'ab' (with ε-transitions)",
                "states": ["q0", "q1", "q2"],
                "alphabet": ["a", "b", "ε"],
                "transitions": {
                    "q0": {"a": ["q0", "q1"], "b": ["q0"]},
                    "q1": {"b": ["q2"]},
                    "q2": {}
                },
                "start_state": "q0",
                "accept_states": ["q2"]
            }
        ]
    }
