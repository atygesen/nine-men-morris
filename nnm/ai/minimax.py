from typing import Sequence

from nnm.rules.rules import CandidateMove, CandidatePlacement, Rules
from nnm.board import Player, Board
from nnm.ai.evaluator import Evaluator

MIN_FLOAT = float("-inf")
MAX_FLOAT = float("inf")


class MinimaxAI:
    def __init__(
        self, me: Player, other: Player, rules: Rules, max_depth: int = 3
    ) -> None:
        self.rules = rules
        self.max_depth = max_depth

        self._cache = dict()
        self.evaluator = Evaluator(self.board, me, other, rules)

    def clear(self):
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
        key = self.board.get_board_state()
        if key in self._cache:
            return self._cache[key]
        
        retval = None

        if self.rules.is_game_over():
            if is_maximizing:
                # TODO:  This value seems to be the wrong way around... but it works??!
                retval = MIN_FLOAT
            else:
                retval = MAX_FLOAT
        elif depth == self.max_depth:
            retval = self.evaluator.evaluate()
            # print("Evaluation:", retval)

        if retval is not None:
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
        self._cache[key] = best_eval
        return best_eval
