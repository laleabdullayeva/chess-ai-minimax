
import chess
from evaluation import evaluate_board

def minimax(board, depth, maximizing_player, stats):

    # Araşdırılan vəziyyətlərin sayını artır
    stats["nodes"] += 1

    # Dayanma şərti
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    # MAX oyunçusu
    if maximizing_player:
        best_score = float("-inf")

        for move in board.legal_moves:
            board.push(move)

            score = minimax(
                board,
                depth - 1,
                False,
                stats
            )

            board.pop()

            best_score = max(best_score, score)

        return best_score
    # MIN oyunçusu
    else:
        best_score = float("inf")

        for move in board.legal_moves:
            board.push(move)

            score = minimax(
                board,
                depth - 1,
                True,
                stats
            )

            board.pop()

            best_score = min(best_score, score)

        return best_score


def find_best_move(board, depth):

    best_move = None
    best_score = float("-inf")

    stats = {"nodes": 0}

    for move in board.legal_moves:
        board.push(move)

        score = minimax(
            board,
            depth - 1,
            False,
            stats
        )

        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

    return best_move, best_score, stats["nodes"]

def alpha_beta(board, depth, alpha, beta, maximizing_player, stats):

    stats["nodes"] += 1

    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        best_score = float("-inf")

        for move in board.legal_moves:
            board.push(move)

            score = alpha_beta(
                board,
                depth - 1,
                alpha,
                beta,
                False,
                stats
            )

            board.pop()

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            # Alpha-Beta pruning
            if beta <= alpha:
                break

        return best_score

    else:
        best_score = float("inf")

        for move in board.legal_moves:
            board.push(move)

            score = alpha_beta(
                board,
                depth - 1,
                alpha,
                beta,
                True,
                stats
            )

            board.pop()

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            # Alpha-Beta pruning
            if beta <= alpha:
                break

        return best_score


def find_best_move_alpha_beta(board, depth):

    best_move = None
    best_score = float("-inf")

    alpha = float("-inf")
    beta = float("inf")

    stats = {"nodes": 0}

    for move in board.legal_moves:
        board.push(move)

        score = alpha_beta(
            board,
            depth - 1,
            alpha,
            beta,
            False,
            stats
        )

        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, best_score)

    return best_move, best_score, stats["nodes"]
