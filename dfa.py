from typing import Dict, List, Set, Optional
from dataclasses import dataclass


@dataclass
class DFADefinition:
    states: List[str]
    alphabet: List[str]
    transitions: Dict[str, Dict[str, str]]  # transitions[state][symbol] = next_state
    start_state: str
    accept_states: List[str]


@dataclass
class SimulationStep:
    step: int
    current_state: str
    symbol_read: Optional[str]
    next_state: Optional[str]
    remaining_input: str
    is_accepted: Optional[bool] = None


def simulate_dfa(dfa: DFADefinition, input_string: str) -> dict:
    steps = []
    current_state = dfa.start_state
    errors = validate_dfa(dfa, input_string)
    if errors:
        return {"success": False, "errors": errors}

    # Initial step
    steps.append(SimulationStep(
        step=0,
        current_state=current_state,
        symbol_read=None,
        next_state=None,
        remaining_input=input_string,
    ).__dict__)

    for i, symbol in enumerate(input_string):
        if symbol not in dfa.alphabet:
            return {
                "success": False,
                "errors": [f"Symbol '{symbol}' not in alphabet {dfa.alphabet}"]
            }

        next_state = dfa.transitions.get(current_state, {}).get(symbol)
        if next_state is None:
            # Dead/trap state - rejection
            steps.append(SimulationStep(
                step=i + 1,
                current_state=current_state,
                symbol_read=symbol,
                next_state="∅ (dead)",
                remaining_input=input_string[i + 1:],
            ).__dict__)
            return {
                "success": True,
                "accepted": False,
                "steps": steps,
                "final_state": current_state,
                "reason": f"No transition from '{current_state}' on '{symbol}'"
            }

        steps.append(SimulationStep(
            step=i + 1,
            current_state=current_state,
            symbol_read=symbol,
            next_state=next_state,
            remaining_input=input_string[i + 1:],
        ).__dict__)
        current_state = next_state

    accepted = current_state in dfa.accept_states
    steps[-1]["is_accepted"] = accepted

    return {
        "success": True,
        "accepted": accepted,
        "steps": steps,
        "final_state": current_state,
        "reason": f"Ended in {'accept' if accepted else 'non-accept'} state '{current_state}'"
    }


def validate_dfa(dfa: DFADefinition, input_string: str = "") -> List[str]:
    errors = []
    if dfa.start_state not in dfa.states:
        errors.append(f"Start state '{dfa.start_state}' not in states list")
    for s in dfa.accept_states:
        if s not in dfa.states:
            errors.append(f"Accept state '{s}' not in states list")
    for state, trans in dfa.transitions.items():
        if state not in dfa.states:
            errors.append(f"Transition references unknown state '{state}'")
        for sym, nxt in trans.items():
            if sym not in dfa.alphabet:
                errors.append(f"Transition symbol '{sym}' not in alphabet")
            if nxt not in dfa.states:
                errors.append(f"Transition target '{nxt}' not in states list")
    return errors
