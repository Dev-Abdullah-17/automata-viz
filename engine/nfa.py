from typing import Dict, List, Set, Optional, FrozenSet
from dataclasses import dataclass, field

EPSILON = "ε"


@dataclass
class NFADefinition:
    states: List[str]
    alphabet: List[str]
    transitions: Dict[str, Dict[str, List[str]]]  # transitions[state][symbol] = [next_states]
    start_state: str
    accept_states: List[str]


def epsilon_closure(states: Set[str], transitions: Dict[str, Dict[str, List[str]]]) -> Set[str]:
    """Compute ε-closure of a set of states."""
    closure = set(states)
    stack = list(states)
    while stack:
        state = stack.pop()
        eps_targets = transitions.get(state, {}).get(EPSILON, [])
        for t in eps_targets:
            if t not in closure:
                closure.add(t)
                stack.append(t)
    return closure


def move(states: Set[str], symbol: str, transitions: Dict[str, Dict[str, List[str]]]) -> Set[str]:
    """Compute move(states, symbol) — all reachable states on symbol."""
    result = set()
    for state in states:
        targets = transitions.get(state, {}).get(symbol, [])
        result.update(targets)
    return result


def simulate_nfa(nfa: NFADefinition, input_string: str) -> dict:
    errors = validate_nfa(nfa)
    if errors:
        return {"success": False, "errors": errors}

    steps = []
    current_states = epsilon_closure({nfa.start_state}, nfa.transitions)

    steps.append({
        "step": 0,
        "active_states": sorted(current_states),
        "symbol_read": None,
        "next_states": None,
        "remaining_input": input_string,
        "note": f"ε-closure({{{nfa.start_state}}}) = {{{', '.join(sorted(current_states))}}}"
    })

    for i, symbol in enumerate(input_string):
        if symbol not in nfa.alphabet:
            return {"success": False, "errors": [f"Symbol '{symbol}' not in alphabet"]}

        moved = move(current_states, symbol, nfa.transitions)
        next_states = epsilon_closure(moved, nfa.transitions)

        steps.append({
            "step": i + 1,
            "active_states": sorted(current_states),
            "symbol_read": symbol,
            "next_states": sorted(next_states),
            "remaining_input": input_string[i + 1:],
            "note": f"move({{{', '.join(sorted(current_states))}}}, '{symbol}') → ε-closure = {{{', '.join(sorted(next_states)) or '∅'}}}"
        })

        current_states = next_states
        if not current_states:
            return {
                "success": True,
                "accepted": False,
                "steps": steps,
                "final_states": [],
                "reason": "Active state set became empty (∅) — rejected"
            }

    accepted = bool(current_states & set(nfa.accept_states))
    accepting_final = sorted(current_states & set(nfa.accept_states))

    return {
        "success": True,
        "accepted": accepted,
        "steps": steps,
        "final_states": sorted(current_states),
        "reason": f"Final states {{{', '.join(sorted(current_states))}}} — {'contains accept state(s): ' + str(accepting_final) if accepted else 'no accept states reached'}"
    }


def validate_nfa(nfa: NFADefinition) -> List[str]:
    errors = []
    if nfa.start_state not in nfa.states:
        errors.append(f"Start state '{nfa.start_state}' not in states")
    for s in nfa.accept_states:
        if s not in nfa.states:
            errors.append(f"Accept state '{s}' not in states")
    return errors
