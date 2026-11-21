
import chess
import time

from minimax import (
    find_best_move,
    find_best_move_alpha_beta
)

board = chess.Board()
depth = 3

# Minimax
start = time.perf_counter()

move1, score1, nodes1 = find_best_move(
    board, depth
)

time1 = time.perf_counter() - start


# Alpha-Beta
start = time.perf_counter()

move2, score2, nodes2 = find_best_move_alpha_beta(
    board, depth
)

time2 = time.perf_counter() - start


print("\n--- MINIMAX ---")
print("Best move:", move1)
print("Score:", score1)
print("Nodes:", nodes1)
print("Time:", round(time1, 4), "seconds")


print("\n--- ALPHA-BETA ---")
print("Best move:", move2)
print("Score:", score2)
print("Nodes:", nodes2)
print("Time:", round(time2, 4), "seconds")


print("\n--- COMPARISON ---")
print("Same move:", move1 == move2)
print("Nodes reduced:", nodes1 - nodes2)
