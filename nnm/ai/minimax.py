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

            self.rules.execute_move(move)  # Will flip the move turn
            score = self.minimax(0, False)
            self.rules.undo_move(move)
            if best_move is None or score > best_score:
                best_score = score
                best_move = move
        return best_move

    def get_hand_pieces(self):
        return [p.pieces_on_hand for p in self.board.players]            

    def get_own_piece_count(self):
        counts = self.board.get_player_piece_counts()
        return counts[self.me]
    
    def get_other_piece_count(self):
        counts = self.board.get_player_piece_counts()
        return counts[self.other]
    
    def get_piece_diff(self) -> int:
        counts = self.board.get_player_piece_counts()
        return counts[self.me] - counts[self.other]

    def minimax(self, depth: int, is_maximizing: bool):
        if self.rules.is_game_over():
            return MAX_FLOAT_LOOPUP[is_maximizing]
        elif depth == self.max_depth:
            return self.get_piece_diff()

        moves = self.rules.iter_current_moves()
        if is_maximizing:
            best_eval = MIN_FLOAT
            for move in moves:
                self.rules.execute_move(move)
                score = self.minimax(depth + 1, False)
                self.rules.undo_move(move)
                best_eval = max(score, best_eval)
        else:
            best_eval = MAX_FLOAT
            for move in moves:
                self.rules.execute_move(move)
                score = self.minimax(depth + 1, True)
                self.rules.undo_move(move)
                best_eval = min(score, best_eval)
        
        return best_eval