from nnm.board import Board, Player
from nnm.consts import ALL_CONNECTED_LINES, DOTS_PARSED
from nnm.rules.rules import Rules, Phase
from nnm_board import Evaluator as CppEvaluator
import random
import json
from pathlib import Path
import functools


class Evaluator:
    def __init__(self, board: Board, me: Player, rules: Rules) -> None:
        self.board = board
        self.me = me
        self.rules = rules
        self._eva = CppEvaluator(self.board._board, self.me.number)

    def reset(self) -> None:
        self._eva.reset()

    def __hash__(self) -> int:
        return self.board.get_board_hash() + 1001235

    def randomize_brain(self) -> None:
        N = self._eva.brain_size()
        brain = []
        for _ in range(N):
            brain.append(random.uniform(0, 10))
        self.set_brain(brain)

    def get_phase(self):
        return self.rules.get_phase()

    def get_brain(self) -> list[float]:
        return self._eva.get_brain()
    
    def set_brain(self, val: list[float]) -> None:
        self._eva.set_brain(val)

    @functools.lru_cache(maxsize=2*2048)
    def evaluate(self) -> float:
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
