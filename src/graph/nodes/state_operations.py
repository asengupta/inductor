from graph.state import CodeExplorerState
from induction_node import InferenceNode


def stack(state: CodeExplorerState) -> list[tuple[InferenceNode, int]]:
    return state["recursion_stack"]


def push(state, node: tuple[InferenceNode, int]) -> None:
    state["recursion_stack"].append(node)


def pop(state) -> tuple[InferenceNode, int]:
    return state["recursion_stack"].pop()


def print_stack(le_stack: list[tuple[InferenceNode, int]]) -> None:
    for st in le_stack:
        print(f"({st[1]}) {st[0].just_str()}")
