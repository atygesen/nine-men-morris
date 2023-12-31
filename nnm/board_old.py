from __future__ import annotations

from typing import TypeAlias, Any
import itertools
import functools

from pathlib import Path
from dataclasses import dataclass, field
from collections import Counter

from nnm.colors import RED, BLUE


import math

BOARD_SIZE = 8

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

@dataclass(slots=True, frozen=True)
class Coord:
    x: float
    y: float

    def as_tuple(self):
        return (self.x, self.y)

    def get_distance(self, other: Coord) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass(slots=True)
class Player:
    name: str
    color: tuple[int, int, int]
    number: int
    pieces_on_hand: int = 9
    ai: Any = None
    _hash: int = field(init=False)

    def __post_init__(self):
        self._hash = hash(self.name)

    def __hash__(self) -> int:
        return self._hash

    def reset(self):
        self.pieces_on_hand = 9

class Board:
    def __init__(self, width, height):
        self.spots = DOTS_PARSED

        self.w = width
        self.h = height

        self.spot_coordinates = [self.as_coord(pos) for pos in self.spots]
        self.connections_coordinates = [
            (self.as_coord(p0), self.as_coord(p1)) for p0, p1 in CONNECTIONS
        ]

        self._turn_index = 0
        self.players = (
            Player(name="Red", color=RED, number=0),
            Player(name="Blue", color=BLUE, number=1),
        )
        self._pieces: dict[SPOT, Player | None] = {spot: None for spot in self.spots}
        # self._pieces: list[Player | None] = [
        #     None for _ in range(BOARD_SIZE * BOARD_SIZE)
        # ]
        self.pieces_by_player = {
            self.players[0]: set(),
            self.players[1]: set(),
        }
        self.ply = 0  # Half moves

        self.connected_spots = {
            s1: {s2 for s2 in self.spots if s1 != s2 and self.is_connected(s1, s2)}
            for s1 in self.spots
        }

        self.central_spots = {s1 for s1 in self.spots if len(self.connected_spots[s1]) == 4}

        self._hash_lu = {
            None: "0",
            self.players[0]: "1",
            self.players[1]: "2",
        }
        self._state_cache = None

    def reset(self):
        for spot in self.spots:
            self.set_spot(spot, None)
        self.pieces_by_player = {
            self.players[0]: set(),
            self.players[1]: set(),
        }
        self.ply = 0
        self._turn_index = 0

        for player in self.players:
            player.reset()

    def toggle_player(self, reverse: bool = False) -> None:
        self._turn_index = (self._turn_index + 1) % 2
        if reverse:
            self.ply -= 1
        else:
            self.ply += 1

    @property
    def pieces(self) -> dict[SPOT, Player | None]:
        return {s: self.get_spot(s) for s in self.spots}

    @property
    def turn(self) -> int:
        return self.ply // 2

    @property
    def player(self) -> Player:
        r = self.players[self._turn_index]
        assert isinstance(r, Player)
        return r

    @property
    def other_player(self) -> Player:
        return self.players[(self._turn_index + 1) % 2]

    def get_closest_spot(self, x: float, y: float) -> SPOT:
        coord = Coord(x, y)
        return min(
            zip(self.spots, self.spot_coordinates),
            key=lambda p: coord.get_distance(p[1]),
        )[0]

    def delete_spot(
        self, spot: SPOT, test_only: bool = False, force: bool = False
    ) -> bool:
        self._state_cache = None
        current = self.get_spot(spot)
        if force:
            if current is not None:
                self.set_spot(spot, None)
                self.pieces_by_player[current].remove(spot)
            return True
        if current is None or current == self.player:
            # Not owned or own spot
            print("Not deleting spot", spot, current, self.player)
            return False
        # Check if the spot is in a three in a line, not allowed to delete.
        if self.has_three_in_a_line(must_contain=spot, player=self.other_player):
            # Check if all of the other players pieces are in a mill
            # If all of that players pieces are in a mill, then we are allowed to delete it.
            other_pieces = self.pieces_by_player[self.other_player]
            if any(
                not self.has_three_in_a_line(must_contain=p, player=self.other_player)
                for p in other_pieces
                if p != spot
            ):
                return False
        if not test_only:
            self.set_spot(spot, None)
            self.pieces_by_player[current].remove(spot)
        return True

    def place_piece(
        self, spot: SPOT, remove_piece: bool = True, player: Player = None
    ) -> bool:
        current = self.get_spot(spot)
        if current is not None:
            return False
        return self.place_piece_no_check(spot, remove_piece=remove_piece, player=player)

    def place_piece_no_check(
        self, spot: SPOT, remove_piece: bool = True, player: Player = None
    ) -> bool:
        self._state_cache = None
        if player is None:
            player = self.player
        self.set_spot(spot, player)
        self.pieces_by_player[player].add(spot)
        if remove_piece:
            if player.pieces_on_hand == 0:
                raise RuntimeError("Cannot place more pieces")
            player.pieces_on_hand -= 1
        return True

    def is_available(self, spot: SPOT) -> bool:
        return self.get_spot(spot) is None

    def as_coord(self, pos: SPOT) -> Coord:
        offset = self._get_offset()
        x = self._i_to_x(pos[0], offset)
        y = self._j_to_y(pos[1], offset)
        return Coord(x, y)

    def _get_offset(self) -> tuple[float, float]:
        offset_x = self.w / 2 - (BOARD_SIZE // 2 * self.w) / BOARD_SIZE
        offset_y = self.h / 2 - (BOARD_SIZE // 2 * self.h) / BOARD_SIZE
        return offset_x, offset_y

    def _i_to_x(self, i: int, offset: tuple[float, float]) -> float:
        # Assume i is [0;7]
        return ((i + 1) * self.w) / BOARD_SIZE + offset[0]

    def _j_to_y(self, j: int, offset: tuple[float, float]) -> float:
        # Assume j is [0;7]
        return ((8 - (j + 1)) * self.h) / BOARD_SIZE + offset[1]

    def has_three_in_a_line(
        self,
        must_contain: SPOT | None = None,
        player: Player | None = None,
    ) -> bool:
        """Check for a three-in-a-line aka. a "mill"."""
        if player is None:
            player = self.player
        player_pieces = self.get_owned_player_spots(player)

        if len(player_pieces) < 3:
            # Not possible to make a mill
            return False

        for p1, p2, p3 in itertools.combinations(player_pieces, 3):
            coord_set = {p1, p2, p3}
            if must_contain and must_contain not in coord_set:
                continue
            if coord_set in ALL_CONNECTED_LINES:
                return True
        return False

    def is_own_piece(self, pos: SPOT) -> bool:
        return self.get_spot(pos) is self.player

    def is_other_player_piece(self, pos: SPOT) -> bool:
        return self.get_spot(pos) is self.other_player

    def is_empty_spot(self, pos: SPOT) -> bool:
        return self.get_spot(pos) is None

    def is_connected(self, p1: SPOT, p2: SPOT) -> bool:
        if p1 == p2:
            # We don't consider self as connected
            return False
        return {p1, p2} in CONNECTIONS

    def move_piece(self, from_pos: SPOT, to_pos: SPOT, flying: bool = False) -> bool:
        if self.is_empty_spot(to_pos) and (
            flying or self.is_connected(from_pos, to_pos)
        ):
            if not self.is_own_piece(from_pos):
                raise RuntimeError("I don't own this piece?")
            self._state_cache = None
            player = self.player
            self.set_spot(from_pos, None)
            self.set_spot(to_pos, player)
            self.pieces_by_player[player].remove(from_pos)
            self.pieces_by_player[player].add(to_pos)
            return True
        return False

    def get_player_piece_counts(self) -> Counter[Player, int]:
        return {p: len(v) for p, v in self.pieces_by_player.items()}

    def get_owned_player_spots(self, player: Player) -> set[SPOT]:
        return self.pieces_by_player[player]

    def get_board_state(self) -> str:
        if self._state_cache:
            return self._state_cache
        t = self._turn_index
        p1 = self.players[0].pieces_on_hand
        p2 = self.players[1].pieces_on_hand

        lu = self._hash_lu
        locs = r"/".join([lu[val] for val in self._pieces.values()])
        state = f"{t:d}_{p1:d}_{p2:d}_{locs}"
        self._state_cache = state
        return state

    def is_spot_owned_by(self, spot: SPOT, player: Player) -> bool:
        return self.get_spot(spot) is player

    def get_spot(self, spot: SPOT) -> Player | None:
        return self._pieces[spot]

    def set_spot(self, spot: SPOT, value: Player | None) -> None:
        self._pieces[spot] = value
