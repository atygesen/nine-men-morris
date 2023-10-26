from __future__ import annotations
import nnm_board
import functools
import operator

from typing import Any

from dataclasses import dataclass, field

from nnm.colors import RED, BLUE

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
    def __init__(self):
        self._board = nnm_board.Board()
        self.players = (
            Player(name="Red", color=RED, number=0),
            Player(name="Blue", color=BLUE, number=1),
        )

        self.all_index = range(24)
        self.connected_spots = {
            s1: {s2 for s2 in self.all_index if s1 != s2 and self.is_connected(s1, s2)}
            for s1 in self.all_index
        }

    def is_connected(self, i1: int, i2: int) -> bool:
        return self._board.is_connected(i1, i2)

    @property
    def current_player(self):
        return self.players[self._turn_index]

    @property
    def other_player(self) -> Player:
        return self.players[(self._turn_index + 1) % 2]

    def get_piece_state(self) -> list[int]:
        return self._board.get_board()

    def place_piece(self, index: int, player: Player | None = None, check_mill: bool = True) -> None | bool:
        if player is None:
            self._board.place_piece(index)
        else:
            self._board.place_piece(index, player.number)
        if check_mill:
            return self._board.check_mill(index, player.number)
        return None
    
    def force_place_piece(self, index: int, player: Player) -> None:
        """Place a piece, but do not take a piece from the hand."""
        self._board.temp_place_piece(index, player.number)

    def move_piece(self, from_pos: int, to_pos: int, player: Player | None = None, flying: bool = False) -> None:
        if flying:
            fnc = self._board.move_piece_flying
        else:
            fnc = self._board.move_piece
        if player is None:
            fnc(from_pos, to_pos)
        else:
            fnc(from_pos, to_pos, player.number)

    def remove_piece(self, pos: int, player: Player | None = None) -> None:
        """Remove a piece from the board"""
        if player is None:
            self._board.remove_piece(pos)
        else:
            self._board.remove_piece(pos, player.number)

    def can_delete(self, pos: int, player: Player | None = None):
        if player is None:
            player = self.current_player
        return self._board.can_delete(pos, player.number)
        
    def force_remove_piece(self, pos: int) -> None:
        self._board.remove_piece(pos, -1)  # Checks it wasn't already empty

    def give_piece(self) -> None:
        self._board.give_piece()

    def is_in_mill(self, pos: int, player: Player) -> bool:
        return self._board.check_mill(pos, player.number)

    def is_available(self, pos: int) -> bool:
        return self._board.is_available(pos)

    def toggle_player(self) -> None:
        self._board.toggle_turn()
    
    def reverse_turn(self):
        self._board.reverse_turn()

    @property
    def _turn_index(self):
        return self._board.turn_index
    
    @property
    def ply(self) -> int:
        return self._board.ply

    def get_board_state(self) -> int:
        def yield_hashes():
            yield self._turn_index
            yield self._board.get_board_hash()
        return functools.reduce(operator.xor, map(hash, yield_hashes()))
    
    def reset(self) -> None:
        self._board.reset()

    def get_board_key(self) -> str:
        t = self._turn_index
        p1, p2 = self.get_piece_counts()

        locs = "/".join(map(str, self._board.get_board()))
        state = f"{t:d}_{p1:d}_{p2:d}_{locs}"
        self._state_cache = state
        return state
    
    def get_player_piece_counts(self, player: Player) -> int:
        return self._board.pieces_on_board(player.number)
    
    def get_piece_counts(self) -> tuple[int, int]:
        return self._board.get_player_one_pieces(), self._board.get_player_two_pieces()
    
    def get_owned_player_spots(self, player: Player) -> list[int]:
        return [idx for idx, owner in enumerate(self.get_piece_state()) if owner == player.number]
    
    def get_owner(self, pos: int) -> Player | None:
        owner = self._board.get_owner(pos)
        if owner == -1:
            return None
        return self.players[owner]
    
    def is_own_piece(self, pos: int) -> bool:
        return self._board.get_owner(pos) == self.current_player.number
