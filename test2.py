import nnm_board
import time

# Creating an instance of the Board class
board = nnm_board.Board()

# print(dir(board))

assert board.is_connected(0, 1)
assert board.is_connected(0, 1) == board.is_connected(1, 0)
# print(board.is_connected(0, 2))


# print(board.is_mill(0, 2, 1))

mf = nnm_board.MoveFinder(board)
print("hash", board.get_board_hash())


print(board.turn_index)

board.toggle_turn()

print(board.turn_index)

board.toggle_turn()

print(board.turn_index)

print(board.ply)

board.reverse_turn()

print(board.ply)

board.place_piece(0, 1)
board.place_piece(1, 1)
board.place_piece(2, 1)

t0 = time.perf_counter()

for _ in range(100000):
    board.check_mill(1, 1)
    board.check_mill(1, 2)
dt = time.perf_counter() - t0
print("hash", board.get_board_hash())


for cand in mf.get_movement_phase_moves(1, False):
    print(cand.from_pos, cand.to_pos)

print(dt)