from nnm.board import Board, Player
from nnm.consts import ALL_CONNECTED_LINES, DOTS_PARSED
from nnm.rules.rules import Rules, Phase
import random
import json
from pathlib import Path
import itertools


class Evaluator:
    def __init__(self, board: Board, me: Player, other: Player, rules: Rules) -> None:
        self.board = board
        self.me = me
        self.other = other
        self.rules = rules

        self.states = [
            "piece_diff",
            "my_blocked",
            "other_blocked",
            "closed_diff",
            "two_piece_me",
            "two_piece_other",
            "central_pieces",
        ]

        self.coefficients = {
            Phase.ONE: {
                "piece_diff": 9,
                "my_blocked": -3,
                "other_blocked": 1,
                "closed_diff": 10,
                "two_piece_me": 4,
                "two_piece_other": -3,
                "central_pieces": 0.1,
            },
            Phase.TWO: {
                "piece_diff": 11,
                "my_blocked": -5,
                "other_blocked": 5,
                "closed_diff": 100,
                "two_piece_me": 3,
                "two_piece_other": -3,
                "central_pieces": 0.0,
            },
            Phase.THREE: {
                "piece_diff": 100,
                "my_blocked": 0,
                "other_blocked": 0,
                "closed_diff": 100,
                "two_piece_me": 3,
                "two_piece_other": -3,
                "central_pieces": 0,
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
            if i == 0:
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
        # print(self.coefficients[phase])
        if phase <= 0:
            return 0
        c = self.coefficients[self.get_phase()]
        score = 0
        score += self._get_piece_diff() * c["piece_diff"]

        # if c1 := c["central_pieces"]:
        #     score += -c1 * self._get_central_pieces(self.me)
        # # More blocked is bad.
        # if c1 := c["my_blocked"]:
        #     score += c1 * self._get_blocked_pieces(self.me)
        # if c1 := c["other_blocked"]:
        #     score += c1 * self._get_blocked_pieces(self.other)
        # if c1 := c["closed_diff"]:
        #     score += c1 * (
        #         self._get_closed_morris(self.me) - self._get_closed_morris(self.other)
        #     )
        # if c1 := c["two_piece_me"]:
        #     score += c1 * self._get_two_piece_config(self.me)
        # if c1 := c["two_piece_other"]:
        #     score += c1 * self._get_two_piece_config(self.other)
        return score

    def _get_central_pieces(self, player: Player) -> int:
        owned = self.board.pieces_by_player[player]
        return len(owned - self.board.central_spots)

    def _get_piece_diff(self) -> int:
        # counts = self.board.get_player_piece_counts()
        fnc = self.board.get_player_piece_counts
        return fnc(self.me) - fnc(self.other)

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
        # BLOCKED_CACHE[key] = n_blocked
        return n_blocked

    def _get_closed_morris(self, player: Player):
        owned_pieces = self.board.pieces_by_player[player]

        tot = 0
        for p1, p2, p3 in itertools.combinations(owned_pieces, 3):
            # Check if on a line
            coord_set = {p1, p2, p3}
            if coord_set in ALL_CONNECTED_LINES:
                tot += 1
        return tot

    def _get_two_piece_config(self, player: Player):
        owned_pieces = self.board.pieces_by_player[player]
        tot = 0
        for p1, p2 in itertools.combinations(owned_pieces, 2):
            if not self.board.is_connected(p1, p2):
                continue
            # Get the third spot to form the line
            pos_set = {p1, p2}
            for line in ALL_CONNECTED_LINES:
                rem = line - pos_set
                if len(rem) == 1:
                    if self.board.get_spot(next(iter(rem))) is None:
                        tot += 1
        return tot

    def load_brain(self, fname="brain.json") -> None:
        p = Path(fname)
        if not p.is_file():
            print("Using default brain")
            # self.randomize_brain()
            return
        with open(fname) as fd:
            brains = json.load(fd)
        for i, brain in enumerate(brains["brains"]):
            score = brains["score"][i]
            if score > 0:
                # print("Setting brain with score", brains["result"][i], brains["turns"][i], score)
                self.set_brain(brain)
