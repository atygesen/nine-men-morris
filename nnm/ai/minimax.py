from typing import Sequence

from nnm.rules.rules import CandidateMove, CandidatePlacement, Rules, Phase
from nnm.board import Player, Board
from nnm.ai.evaluator import Evaluator

MIN_FLOAT = float("-inf")
MAX_FLOAT = float("inf")


class MinimaxAI:
    def __init__(
        self, me: Player, rules: Rules, max_depth: int = 3
    ) -> None:
        self.rules = rules
        self.max_depth = max_depth
        self.me = me
        self._cache = dict()
        self.evaluator = Evaluator(self.board, me, rules)

    def clear(self) -> None:
        self._cache.clear()

    @property
    def board(self) -> Board:
        return self.rules.board

    def select_move(
        self, moves: Sequence[CandidatePlacement] | Sequence[CandidateMove]
    ):
        best_score = MIN_FLOAT
        best_move = None
        for move in moves:
            self.rules.execute_move(move)
            score = self.minimax(0, MIN_FLOAT, MAX_FLOAT, False)
            self.rules.undo_move(move)
            if best_move is None or score > best_score:
                best_score = score
                best_move = move
        return best_move

    def get_hand_pieces(self):
        return self.board.get_piece_counts()

    def minimax(self, depth: int, alpha: float, beta: float, is_maximizing: bool):
        key = self.board.get_board_hash()
        if key in self._cache:
            return self._cache[key]
        
        retval = None
        phase = self.rules.get_phase()
        if phase is Phase.DRAW:
            retval = 0.0
        elif phase is Phase.DONE:
            if self.board.get_player_pieces_on_board(self.me) > 2:
                # Win
                retval = MAX_FLOAT
            else:
                # Loss
                retval = MIN_FLOAT
        elif depth == self.max_depth:
            retval = self.evaluator.evaluate()

        if retval is not None:
            # We cache any static evaluations, but not results of a branch
            self._cache[key] = retval
            return retval

        # Figure out the optimization rules
        moves = self.rules.get_current_player_moves()
        if is_maximizing:
            best_eval = MIN_FLOAT
            for move in moves:
                self.rules.execute_move(move)
                score = self.minimax(depth + 1, alpha, beta, False)
                self.rules.undo_move(move)
                best_eval = max(score, best_eval)
                if best_eval > beta:
                    break
                alpha = max(alpha, best_eval)
        else:
            best_eval = MAX_FLOAT
            for move in moves:
                self.rules.execute_move(move)
                score = self.minimax(depth + 1, alpha, beta, True)
                self.rules.undo_move(move)
                best_eval = min(score, best_eval)
                if best_eval < alpha:
                    break
                beta = min(beta, best_eval)
        return best_eval
