from typing import Sequence

from nnm.rules.rules import CandidateMove, CandidatePlacement, Rules
from nnm.board import Player, Board

MIN_FLOAT = float("-inf")
MAX_FLOAT = float("inf")

MAX_FLOAT_LOOPUP = {
    True: MAX_FLOAT,
    False: MIN_FLOAT,
}

class MinimaxAI:

    def __init__(self, me: Player, other: Player, rules: Rules, max_depth: int=3) -> None:
        self.rules = rules
        self.max_depth = max_depth
        self.me = me
        self.other = other

    @property
    def board(self) -> Board:
        return self.rules.board

    def select_move(self, moves: Sequence[CandidatePlacement] | Sequence[CandidateMove]):
        best_score = float("-inf")
        best_move = None
        for move in moves:
            with self.rules.try_move(move):  # Will flip the move turn
                score = self.minimax(0, MIN_FLOAT, MAX_FLOAT, False)
            if best_move is None or score > best_score:
                best_score = score
                best_move = move
        return best_move

    def get_hand_pieces(self):
        return [p.pieces_on_hand for p in self.board.players]            
  
    def get_piece_diff(self) -> int:
        counts = self.board.get_player_piece_counts()
        return counts[self.me] - counts[self.other]

    def minimax(self, depth: int, alpha: float, beta: float, is_maximizing: bool):
        if self.rules.is_game_over():
            if is_maximizing:
                return MIN_FLOAT
            else:
                return MAX_FLOAT
        elif depth == self.max_depth:
            return self.get_piece_diff()

        # Figure out the optimization rules
        if is_maximizing:
            best_eval = MIN_FLOAT
            eva_fnc = max
        else:
            best_eval = MAX_FLOAT
            eva_fnc = min
        moves = self.rules.get_current_player_moves()
        for move in moves:
            with self.rules.try_move(move):
                score = self.minimax(depth + 1, alpha, beta, False)
            best_eval = eva_fnc(score, best_eval)
            alpha = eva_fnc(alpha, score)
            if beta <= alpha:
                break
        return best_eval