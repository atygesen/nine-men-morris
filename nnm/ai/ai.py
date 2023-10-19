from typing import Protocol, Sequence

from nnm.rules.rules import CandidateMove, CandidatePlacement

class AI(Protocol):

    def select_move(self, moves: Sequence[CandidatePlacement] | Sequence[CandidateMove]):
        ...