from nnm.board import Board, Player
from nnm.rules.rules import Rules, Phase
import random


class Evaluator:
    def __init__(self, board: Board, me: Player, other: Player, rules: Rules) -> None:
        self.board = board
        self.me = me
        self.other = other
        self.rules = rules

        self.states = ["piece_diff", "my_blocked", "other_blocked"]

        self.coefficients = {
            Phase.ONE: {
                "piece_diff": 9,
                "my_blocked": -1,
                "other_blocked": 1,
            },
            Phase.TWO: {
                "piece_diff": 11,
                "my_blocked": -5,
                "other_blocked": 5,
            },
            Phase.THREE: {
                "piece_diff": 100,
                "my_blocked": 0,
                "other_blocked": 0,
            },
        }

    def get_phase(self):
        return self.rules.get_phase()
    
    def randomize_brain(self) -> None:
        for coef in self.coefficients.values():
            coef["piece_diff"] = random.uniform(0, 10)
            coef["my_blocked"] = random.uniform(-10, 0)
            coef["other_blocked"] = random.uniform(0, 10)

    def set_brain(self, arr: list[float]) -> None:
        N = len(self.states)
        for ii, val in enumerate(arr):
            i, j = divmod(ii, N)
            if i  == 0:
                p = Phase.ONE
            elif i == 1:
                p = Phase.TWO
            else:
                p = Phase.THREE
            state = self.states[j]
            self.coefficients[p][state] = val         

    def get_brain(self) -> list[float]:
        brain = []
        for coef in self.coefficients.values():
            for val in coef.values():
                brain.append(val)
        return brain

    def evaluate(self) -> float:
        phase = self.get_phase()
        if phase <= 0:
            return 0
        c = self.coefficients[self.get_phase()]
        score = 0
        score += self._get_piece_diff() * c["piece_diff"]

        # More blocked is bad.
        if (c1 := c["my_blocked"]):
            score += c1 * self._get_blocked_pieces(self.me)
        if (c1 := c["other_blocked"]):
            score += c1 * self._get_blocked_pieces(self.other)
        return score

    def _get_piece_diff(self) -> int:
        counts = self.board.get_player_piece_counts()
        return counts[self.me] - counts[self.other]

    def _get_other_player(self, player: Player):
        return self.me if player is self.other else self.other

    def _get_blocked_pieces(self, player: Player):
        owned_pieces = self.board.pieces_by_player[player]

        other_player = self._get_other_player(player)
        other_player_pieces = self.board.pieces_by_player[other_player]

        n_blocked = 0
        for spot in owned_pieces:
            connected = self.board.connected_spots[spot]
            if not connected - other_player_pieces:
                n_blocked += 1
        return n_blocked
