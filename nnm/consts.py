from __future__ import annotations

from typing import TypeAlias
import itertools
from pathlib import Path

SPOT: TypeAlias = tuple[int, int]

DOTS = (
    "a1",
    "d1",
    "g1",
    "b2",
    "d2",
    "f2",
    "c3",
    "d3",
    "e3",
    "a4",
    "b4",
    "c4",
    "e4",
    "f4",
    "g4",
    "c5",
    "d5",
    "e5",
    "b6",
    "d6",
    "f6",
    "a7",
    "d7",
    "g7",
)


def _parse_coord(dot: str) -> SPOT:
    CONVERT = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6}
    return CONVERT[dot[0]], int(dot[1]) - 1


DOTS_PARSED = [_parse_coord(dot) for dot in DOTS]
DOTS_PARSED.sort()

with Path(__file__).with_name("connections.txt").open() as fd:
    CONNECTIONS_RAW = [line.strip().split(" ") for line in fd if line.strip()]
    CONNECTIONS = [set(map(_parse_coord, c)) for c in CONNECTIONS_RAW]
    del CONNECTIONS_RAW
INDEX_TO_SPOT: dict[int, SPOT] = {i: spot for i, spot in enumerate(DOTS_PARSED)}
SPOT_TO_INDEX: dict[SPOT, int] = {spot: i for i, spot in enumerate(DOTS_PARSED)}

def _is_a_connected_line(p1: SPOT, p2: SPOT, p3: SPOT) -> bool:
    # Check all of either i or j coordinates are equal (must be on a line)
    for idx in (0, 1):
        if p1[idx] == p2[idx] and p1[idx] == p3[idx]:
            break
    else:
        return False

    # # Check they are pairwise connected
    for a, b, c in itertools.permutations([p1, p2, p3], 3):
        if {a, b} in CONNECTIONS and {b, c} in CONNECTIONS:
            return True
    return False

ALL_CONNECTED_LINES = [
    {p1, p2, p3}
    for p1, p2, p3 in itertools.combinations(DOTS_PARSED, 3)
    if _is_a_connected_line(p1, p2, p3)
]
