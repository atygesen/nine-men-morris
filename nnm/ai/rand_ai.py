
from typing import Iterable
import random

from nnm.rules.rules import CandidateMove, CandidatePlacement

class RandomAI:

    def select_move(self, moves: Iterable[CandidatePlacement] | Iterable[CandidateMove]):
        return random.choice(list(moves))
    