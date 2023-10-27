from typing import TypeAlias, Iterator
from enum import IntEnum
from dataclasses import dataclass
from collections import Counter

from nnm_board import (
    MoveFinder,
    CppCandidateMove as CandidateMove,
    CppCandidatePlacement as CandidatePlacement,
)


from nnm.board import Board

SPOT: TypeAlias = tuple[int, int]
EMPTY = -1


class Phase(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    DONE = -1
    DRAW = -2


# @dataclass(slots=True)
# class CandidatePlacement:
#     spot: int
#     delete_spot: int = EMPTY


# @dataclass(slots=True)
# class CandidateMove:
#     from_spot: int
#     to_spot: int
#     delete_spot: int = EMPTY


# P1_MOVE_CACHE = {}


class Rules:
    def __init__(self, board: Board):
        self.board = board
        self._state_counter = Counter()
        self._move_finder = MoveFinder(board._board)
        self._is_draw = False

    def reset(self):
        self._state_counter.clear()
        self._is_draw = False

    def get_current_player_moves(
        self,
    ) -> list[CandidatePlacement] | list[CandidateMove]:
        phase = self.get_phase()
        if phase is Phase.DONE:
            return []

        if phase is Phase.ONE:
            return self.get_phase_one_moves()
        elif phase is Phase.TWO:
            return self.get_phase_two_moves()
        else:
            return self.get_phase_three_moves()

    def iter_current_moves(self):
        phase = self.get_phase()
        if phase is Phase.DONE:
            return []

        if phase is Phase.ONE:
            yield from self.iter_phase_one_moves()
        elif phase is Phase.TWO:
            yield from self.iter_phase_two_three_moves(phase=Phase.TWO)
        else:
            yield from self.iter_phase_two_three_moves(phase=Phase.THREE)

    @property
    def turn(self) -> int:
        return self.board.turn

    @property
    def current_player(self):
        return self.board.current_player

    @property
    def other_player(self):
        return self.board.other_player

    def get_phase(self) -> Phase:
        if self._is_draw:
            return Phase.DRAW
        return Phase(self._move_finder.get_phase())

    def _iter_to_delete(self):
        for to_delete in self.board.get_owned_player_spots(player=self.other_player):
            can_delete = self.board.can_delete(to_delete, self.current_player)
            # can_delete = self.board.delete_spot(to_delete, test_only=True)
            if can_delete:
                yield to_delete

    def get_phase_one_moves(self) -> list[CandidatePlacement]:
        return self._move_finder.get_phase_one_moves(self.current_player.number)

    def iter_phase_one_moves(self):
        for move in self._move_finder.get_phase_one_moves(self.current_player.number):
            yield move

    def iter_phase_two_three_moves(self, phase=Phase.TWO) -> Iterator[CandidateMove]:
        is_flying = phase is Phase.THREE
        for cand in self._move_finder.get_movement_phase_moves(
            self.current_player.number, is_flying
        ):
            yield cand

    def get_phase_two_moves(self) -> list[CandidateMove]:
        return self._move_finder.get_movement_phase_moves(
            self.current_player.number, False
        )

    def get_phase_three_moves(self) -> list[CandidateMove]:
        return self._move_finder.get_movement_phase_moves(
            self.current_player.number, True
        )

    def execute_move(self, move) -> None:
        self.board.execute_move(move)

    def undo_move(self, move):
        self.board.undo_move(move)

    def is_game_over(self) -> bool:
        phase = self.get_phase()
        if phase is Phase.DONE or phase is Phase.DRAW:
            return True
        if phase is Phase.ONE:
            # Game can never be over in phase 1
            return False
        for _ in self.iter_current_moves():
            # If there is any valid move, we aren't done.
            return False
        return True

    def next_turn(self) -> None:
        if self._is_draw:
            raise RuntimeError("Game is a draw, cannot start next turn")
        state = self.board.get_board_hash()
        self._state_counter[state] += 1
        if self._state_counter[state] >= 3:
            self._is_draw = True
