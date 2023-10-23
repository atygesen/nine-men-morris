import random
import numpy as np

class GA:
    def __init__(self, n_pops=10) -> None:
        self.n_pops = n_pops
        self.generation = -1
        self.gen_pop = None
        self.scores = []

    def generate_pops(self, arr: list[float]):
        self.generation += 1
        pops = [arr.copy()]
        if self.scores:
            pops.append(self.make_child())
        for _ in range(self.n_pops - len(pops)):
            new = self.mutate(arr)
            pops.append(new)
        self.gen_pop = pops
        return pops
    
    def make_child(self) -> list[float]:
        # combine two best
        idx = np.argsort(self.scores)
        child = (np.array(self.gen_pop[idx[-1]]) + np.array(self.gen_pop[idx[-2]])) / 2
        child = list(child)
        return child


    def mutate(self, arr: list[float]) -> list[float]:
        cpy = arr.copy()
        n_mutations = random.randint(1, len(arr))
        indx = random.sample(range(len(arr)), n_mutations)
        for i in indx:
            if random.random() < 0.2:
                cpy[i] = random.uniform(-10, 10)
            else:
                cpy[i] += random.uniform(-1, 1)
        return cpy