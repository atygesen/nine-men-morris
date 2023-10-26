from nnm.board import Board, Player
from nnm.consts import ALL_CONNECTED_LINES, DOTS_PARSED
from nnm.rules.rules import Rules, Phase
from nnm_board import Evaluator as CppEvaluator
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
        self._eva = CppEvaluator(self.board._board, self.me.number, self.other.number)

    def randomize_brain(self) -> None:
        N = self._eva.brain_size()
        brain = []
        for _ in range(N):
            brain.append(random.uniform(-10, 10))
        self.set_brain(brain)

    def get_phase(self):
        return self.rules.get_phase()

    def get_brain(self) -> list[float]:
        return self._eva.get_brain()
    
    def set_brain(self, val: list[float]) -> None:
        self._eva.set_brain(val)

    def evaluate(self) -> float:
        phase = self.get_phase()
        # print(self.coefficients[phase])
        if phase <= 0:
            return 0
        return self._eva.evaluate()

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
