import random

class GA:
    def __init__(self, n_pops=10) -> None:
        self.n_pops = n_pops
        self.generation = 0

    def generate_pops(self, arr: list[float]):
        self.generation += 1
        pops = [arr.copy()]
        for _ in range(self.n_pops - 1):
            new = self.mutate(arr)
            pops.append(new)
        return pops

    def mutate(self, arr: list[float]) -> list[float]:
        cpy = arr.copy()
        n_mutations = random.randint(1, min(3, len(arr)))
        indx = random.sample(range(len(arr)), n_mutations)
        for i in indx:
            if random.random() < 0.2:
                cpy[i] = random.uniform(-10, 10)
            else:
                cpy[i] += random.uniform(-1, 1)
        return cpy