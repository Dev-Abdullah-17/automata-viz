from typing import Dict, List, Set, FrozenSet
from nfa import NFADefinition, epsilon_closure, move, EPSILON


def nfa_to_dfa(nfa: NFADefinition) -> dict:
    """
    Convert NFA to DFA using the Subset Construction algorithm.
    Returns the DFA definition + a trace of the construction steps.
    """
    construction_steps = []

    # Step 1: start state = ε-closure of NFA start state
    start_closure = frozenset(epsilon_closure({nfa.start_state}, nfa.transitions))
    
    dfa_states_map: Dict[FrozenSet, str] = {}  # frozenset → DFA state name
    unmarked = [start_closure]
    dfa_transitions: Dict[str, Dict[str, str]] = {}
    dfa_accept_states = []

    def state_name(fs: FrozenSet) -> str:
        return "{" + ", ".join(sorted(fs)) + "}"

    dfa_states_map[start_closure] = state_name(start_closure)
    construction_steps.append({
        "action": "start",
        "description": f"ε-closure({{{nfa.start_state}}}) = {state_name(start_closure)} → DFA start state"
    })

    while unmarked:
        current_set = unmarked.pop(0)
        current_name = dfa_states_map[current_set]
        dfa_transitions[current_name] = {}

        for symbol in nfa.alphabet:
            if symbol == EPSILON:
                continue

            moved = move(set(current_set), symbol, nfa.transitions)
            next_set = frozenset(epsilon_closure(moved, nfa.transitions))
            next_name = state_name(next_set) if next_set else "∅"

            construction_steps.append({
                "action": "transition",
                "from_state": current_name,
                "symbol": symbol,
                "move_result": "{" + ", ".join(sorted(moved)) + "}" if moved else "∅",
                "epsilon_closure": next_name,
                "description": f"δ({current_name}, {symbol}) = move+ε-closure = {next_name}"
            })

            if next_set:
                if next_set not in dfa_states_map:
                    dfa_states_map[next_set] = next_name
                    unmarked.append(next_set)
                    construction_steps.append({
                        "action": "new_state",
                        "state": next_name,
                        "description": f"New DFA state discovered: {next_name}"
                    })
                dfa_transitions[current_name][symbol] = next_name
            else:
                dfa_transitions[current_name][symbol] = "∅"

    # Determine DFA accept states
    for nfa_set, dfa_name in dfa_states_map.items():
        if nfa_set & set(nfa.accept_states):
            dfa_accept_states.append(dfa_name)

    dfa_states = list(dfa_states_map.values())
    dfa_start = dfa_states_map[start_closure]

    return {
        "success": True,
        "dfa": {
            "states": dfa_states,
            "alphabet": [s for s in nfa.alphabet if s != EPSILON],
            "transitions": dfa_transitions,
            "start_state": dfa_start,
            "accept_states": dfa_accept_states
        },
        "construction_steps": construction_steps,
        "summary": {
            "nfa_states_count": len(nfa.states),
            "dfa_states_count": len(dfa_states),
            "description": "Subset construction complete"
        }
    }
