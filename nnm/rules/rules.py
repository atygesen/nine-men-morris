from typing import TypeAlias, Iterator
from enum import IntEnum
from dataclasses import dataclass
from contextlib import contextmanager
from collections import Counter


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


class Rules:
    def __init__(self, board: Board):
        self.board = board
        self._state_counter = Counter()

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
        return self.board.player

    @property
    def other_player(self):
        return self.board.other_player

    def get_phase(self) -> Phase:
        # Check if the player has any pieces on hand
        player = self.current_player
        if player.pieces_on_hand > 0:
            return Phase.ONE

        # Cannot be a draw in phase 1
        high_state = self._state_counter.most_common(1)
        if high_state and high_state[0][1] >= 3:
            return Phase.DRAW

        # Check pieces on the board
        player_piece_count = self.board.get_player_piece_counts()[player]
        if player_piece_count < 3:
            return Phase.DONE
        elif player_piece_count == 3:
            return Phase.THREE

        return Phase.TWO

    def _iter_to_delete(self):
        for to_delete in self.board.get_owned_player_spots(player=self.other_player):
            can_delete = self.board.delete_spot(to_delete, test_only=True)
            if can_delete:
                yield to_delete

    def get_phase_one_moves(self) -> list[CandidatePlacement]:
        # Available positions to place in phase 1
        moves = list(self.iter_phase_one_moves())
        # First check moves which delete spots
        moves.sort(key=lambda cand: cand.delete_spot is None)
        return moves

    def iter_phase_one_moves(self):
        for spot, owner in self.board.pieces.items():
            if owner is not None:
                continue
            # Check if we made a mill
            self.board.place_piece_no_check(spot, remove_piece=False)
            if self.board.has_three_in_a_line(
                must_contain=spot, player=self.current_player
            ):
                for to_delete in self._iter_to_delete():
                    yield CandidatePlacement(spot, delete_spot=to_delete)
            else:
                yield CandidatePlacement(spot)
            self.board.delete_spot(spot, force=True)
            
    def iter_phase_two_three_moves(self, phase=Phase.TWO) -> Iterator[CandidateMove]:
        current_pices = self.board.get_owned_player_spots(self.current_player)

        for from_spot in current_pices:
            # Get all connected spots to this piece
            if phase is Phase.TWO:
                to_spots = self.board.connected_spots[from_spot]
            else:
                to_spots = self.board.spots
            for to_spot in to_spots:
                if not self.board.is_empty_spot(to_spot):
                    continue
                self.board.move_piece(from_spot, to_spot, flying=True)
                moves = []
                if self.board.has_three_in_a_line(
                    must_contain=to_spot, player=self.current_player
                ):
                    for to_delete in self._iter_to_delete():
                        moves.append(
                            CandidateMove(
                                from_spot=from_spot,
                                to_spot=to_spot,
                                delete_spot=to_delete,
                            )
                        )
                else:
                    moves.append(CandidateMove(from_spot=from_spot, to_spot=to_spot))
                self.board.move_piece(to_spot, from_spot, flying=True)
                yield from moves

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
            self.board.place_piece_no_check(move.spot)
        elif isinstance(move, CandidateMove):
            flying = self.get_phase() is Phase.THREE
            self.board.move_piece(move.from_spot, move.to_spot, flying=flying)
        else:
            raise TypeError(f"Unknown move: {move!r}")
        if move.delete_spot:
            self.board.delete_spot(move.delete_spot)

        self.board.toggle_player()

    def undo_move(self, move: CandidateMove | CandidatePlacement) -> None:
        self.board.toggle_player(reverse=True)
        if isinstance(move, CandidatePlacement):
            self.board.delete_spot(move.spot, force=True)
            self.current_player.pieces_on_hand += 1
        elif isinstance(move, CandidateMove):
            self.board.move_piece(move.to_spot, move.from_spot, flying=True)
        else:
            raise TypeError(f"Unknown move: {move!r}")

        if move.delete_spot:
            self.board.place_piece(
                move.delete_spot, remove_piece=False, player=self.other_player
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

    @contextmanager
    def try_move(self, move):
        self.execute_move(move)
        yield
        self.undo_move(move)

    def next_turn(self):
        state = self.board.get_board_state()
        self._state_counter[state] += 1
