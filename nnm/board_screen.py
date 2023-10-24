from __future__ import annotations

from typing import TypeAlias, Any
import itertools
import functools

from pathlib import Path
from dataclasses import dataclass
from nnm.board import Board, Player
from nnm.consts import DOTS_PARSED, CONNECTIONS, INDEX_TO_SPOT, SPOT_TO_INDEX


import math

SPOT: TypeAlias = tuple[int, int]

BOARD_SIZE = 8


@dataclass(slots=True, frozen=True)
class Coord:
    x: float
    y: float
    index: int | None = None

    def as_tuple(self):
        return (self.x, self.y)

    def get_distance(self, other: Coord) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class BoardScreen:
    def __init__(self, width, height, board: Board):
        self.w = width
        self.h = height
        self.board = board

        self.indices = range(len(DOTS_PARSED))
        self.spot_coordinates = [self.as_coord(pos) for pos in DOTS_PARSED]
        self.connections_coordinates = [
            (self.as_coord(p0), self.as_coord(p1)) for p0, p1 in CONNECTIONS
        ]

    def get_piece_coords(self) -> list[tuple[Coord, Player]]:
        state = self.board.get_piece_state()
        # print(state)
        coords = []

        for ii, owner_num in enumerate(state):
            if owner_num == -1:
                continue
            owner = self.board.players[owner_num]
            coord = self.as_coord(INDEX_TO_SPOT[ii])
            coords.append((coord, owner))
        return coords

    def as_coord(self, pos: SPOT) -> Coord:
        offset = self._get_offset()
        x = self._i_to_x(pos[1], offset)
        y = self._j_to_y(pos[0], offset)
        return Coord(x, y, SPOT_TO_INDEX[pos])

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

    def get_closest_index(self, x: float, y: float) -> int:
        coord = Coord(x, y)
        return SPOT_TO_INDEX[
            min(
                zip(DOTS_PARSED, self.spot_coordinates),
                key=lambda p: coord.get_distance(p[1]),
            )[0]
        ]
