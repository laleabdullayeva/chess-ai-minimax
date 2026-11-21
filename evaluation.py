import chess
# Şahmat fiqurlarının dəyərləri
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}


def evaluate_board(board):
    # Oyun bitibsə, nəticəni yoxla
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -1000
        else:
            return 1000

    if board.is_game_over():
        return 0

    score = 0

    # Lövhədəki bütün fiqurları yoxla
    for piece in board.piece_map().values():
        value = PIECE_VALUES[piece.piece_type]

        if piece.color == chess.WHITE:
            score += value
        else:
            score -= value

    return score