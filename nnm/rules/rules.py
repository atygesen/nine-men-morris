from typing import TypeAlias, Iterator
from enum import IntEnum
from dataclasses import dataclass
from collections import Counter

from nnm_board import MoveFinder


from nnm.board import Board

SPOT: TypeAlias = tuple[int, int]


class Phase(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    DONE = -1
    DRAW = -2


@dataclass(slots=True)
class CandidatePlacement:
    spot: SPOT
    delete_spot: SPOT | None = None


@dataclass(slots=True)
class CandidateMove:
    from_spot: SPOT
    to_spot: SPOT
    delete_spot: SPOT | None = None


P1_MOVE_CACHE = {}


class Rules:
    def __init__(self, board: Board):
        self.board = board
        self._state_counter = Counter()
        self._move_finder = MoveFinder(board._board)

    def reset(self):
        self._state_counter.clear()

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
        p = self._move_finder.get_phase()
        if p == 1:
            # No draws in Phase 1, short circuit
            return Phase.ONE
        # Check for draws
        high_state = self._state_counter.most_common(1)
        if high_state and high_state[0][1] >= 3:
            return Phase.DRAW
        return Phase(p)



    def _iter_to_delete(self):
        for to_delete in self.board.get_owned_player_spots(player=self.other_player):
            can_delete = self.board.can_delete(to_delete, self.current_player)
            # can_delete = self.board.delete_spot(to_delete, test_only=True)
            if can_delete:
                yield to_delete

    def get_phase_one_moves(self) -> list[CandidatePlacement]:
        # Available positions to place in phase 1
        moves = list(self.iter_phase_one_moves())
        # First check moves which delete spots
        moves.sort(key=lambda cand: cand.delete_spot is None)
        return moves

    def iter_phase_one_moves(self):
        for move, to_delete in self._move_finder.get_phase_one_moves(self.current_player.number):
            if to_delete == -1:
                to_delete = None
            yield CandidatePlacement(move, delete_spot=to_delete)

    def iter_phase_two_three_moves(self, phase=Phase.TWO) -> Iterator[CandidateMove]:
        is_flying = phase is Phase.THREE
        for cand in self._move_finder.get_movement_phase_moves(self.current_player.number, is_flying):
            to_delete = cand.delete_pos
            if to_delete == -1:
                to_delete = None
            yield CandidateMove(cand.from_pos, cand.to_pos, to_delete)

    def get_phase_two_moves(self) -> list[CandidateMove]:
        moves = list(self.iter_phase_two_three_moves(phase=Phase.TWO))
        moves.sort(key=lambda cand: cand.delete_spot is None)
        return moves

    def get_phase_three_moves(self) -> list[CandidateMove]:
        moves = list(self.iter_phase_two_three_moves(phase=Phase.THREE))
        moves.sort(key=lambda cand: cand.delete_spot is None)
        return moves

    def execute_move(self, move: CandidateMove | CandidatePlacement) -> None:
        if isinstance(move, CandidatePlacement):
            self.board.place_piece(move.spot, check_mill=False)
        elif isinstance(move, CandidateMove):
            flying = self.get_phase() is Phase.THREE
            self.board.move_piece(move.from_spot, move.to_spot, flying=flying)
        else:
            raise TypeError(f"Unknown move: {move!r}")
        if move.delete_spot:
            self.board.force_remove_piece(move.delete_spot)

        self.board.toggle_player()

    def undo_move(self, move: CandidateMove | CandidatePlacement) -> None:
        board = self.board
        board.reverse_turn()
        if isinstance(move, CandidatePlacement):
            board.force_remove_piece(move.spot)
            board.give_piece()
        elif isinstance(move, CandidateMove):
            board.move_piece(move.to_spot, move.from_spot, flying=True)
        else:
            raise TypeError(f"Unknown move: {move!r}")

        if move.delete_spot:
            board.force_place_piece(
                move.delete_spot,
                player=self.other_player,
            )

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

    def next_turn(self):
        state = self.board.get_board_state()
        self._state_counter[state] += 1
