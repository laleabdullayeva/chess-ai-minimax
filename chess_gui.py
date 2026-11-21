
import pygame
import chess
import threading
import queue
import time

# ---------------- SETTINGS ----------------

WIDTH = 720
HEIGHT = 680
BOARD_SIZE = 600
SQUARE_SIZE = BOARD_SIZE // 8

AI_DEPTH = 3

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
BACKGROUND = (35, 35, 35)
TEXT_COLOR = (245, 245, 245)
SELECT_COLOR = (80, 180, 90)
MOVE_COLOR = (100, 160, 220)

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

PIECE_SYMBOLS = {
    "K": "♔", "Q": "♕", "R": "♖",
    "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜",
    "b": "♝", "n": "♞", "p": "♟"
}

# ---------------- INITIALIZATION ----------------

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess AI - Minimax & Alpha-Beta")

clock = pygame.time.Clock()

piece_font = pygame.font.SysFont("segoeuisymbol", 58)
info_font = pygame.font.SysFont("arial", 22)

board = chess.Board()

selected_square = None
legal_moves = []

ai_thinking = False
ai_queue = queue.Queue()

last_nodes = 0
last_time = 0.0


# ---------------- EVALUATION ----------------

def evaluate_board(position):
    """
    Board vəziyyətini qiymətləndirir.
    Müsbət nəticə White üçün,
    mənfi nəticə Black üçün üstünlük deməkdir.
    """

    if position.is_checkmate():
        if position.turn == chess.WHITE:
            return -100000
        else:
            return 100000

    if position.is_game_over():
        return 0

    score = 0

    for piece_type, value in PIECE_VALUES.items():

        white_pieces = position.pieces(
            piece_type, chess.WHITE
        )

        black_pieces = position.pieces(
            piece_type, chess.BLACK
        )

        score += len(white_pieces) * value
        score -= len(black_pieces) * value

    return score


# ---------------- ALPHA-BETA ----------------

def alpha_beta(position, depth, alpha, beta, nodes):
    """
    Alpha-Beta Pruning alqoritmi.
    """

    nodes[0] += 1

    if depth == 0 or position.is_game_over():
        return evaluate_board(position)

    if position.turn == chess.WHITE:
        best_score = -float("inf")

        for move in position.legal_moves:
            position.push(move)

            score = alpha_beta(
                position,
                depth - 1,
                alpha,
                beta,
                nodes
            )

            position.pop()

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if beta <= alpha:
                break

        return best_score

    else:
        best_score = float("inf")

        for move in position.legal_moves:
            position.push(move)

            score = alpha_beta(
                position,
                depth - 1,
                alpha,
                beta,
                nodes
            )

            position.pop()

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            if beta <= alpha:
                break

        return best_score


# ---------------- AI MOVE ----------------

def calculate_ai_move(position):
    """
    AI qara fiqurlarla oynayır.
    Ən yaxşı gedişi Alpha-Beta ilə seçir.
    """

    nodes = [0]
    best_move = None
    best_score = float("inf")

    start_time = time.perf_counter()

    possible_moves = list(position.legal_moves)

    for move in possible_moves:

        position.push(move)

        score = alpha_beta(
            position,
            AI_DEPTH - 1,
            -float("inf"),
            float("inf"),
            nodes
        )

        position.pop()

        if score < best_score:
            best_score = score
            best_move = move

    elapsed = time.perf_counter() - start_time

    return best_move, nodes[0], elapsed


def ai_worker(position_copy):
    """
    AI hesablamasını ayrıca thread-də aparır.
    Bu, Pygame pəncərəsinin donmasının qarşısını alır.
    """

    result = calculate_ai_move(position_copy)

    ai_queue.put(result)


def start_ai():
    global ai_thinking

    if board.is_game_over():
        return

    ai_thinking = True

    position_copy = board.copy()

    thread = threading.Thread(
        target=ai_worker,
        args=(position_copy,),
        daemon=True
    )

    thread.start()


# ---------------- DRAW BOARD ----------------

def draw_board():
    for row in range(8):
        for col in range(8):

            x = col * SQUARE_SIZE
            y = row * SQUARE_SIZE

            if (row + col) % 2 == 0:
                color = LIGHT_SQUARE
            else:
                color = DARK_SQUARE

            pygame.draw.rect(
                screen,
                color,
                (x, y, SQUARE_SIZE, SQUARE_SIZE)
            )


# ---------------- DRAW PIECES ----------------

def draw_pieces():
    for square in chess.SQUARES:

        piece = board.piece_at(square)

        if piece is None:
            continue

        row = 7 - chess.square_rank(square)
        col = chess.square_file(square)

        x = col * SQUARE_SIZE
        y = row * SQUARE_SIZE

        symbol = PIECE_SYMBOLS[piece.symbol()]

        piece_surface = piece_font.render(
            symbol,
            True,
            (20, 20, 20) if piece.color == chess.BLACK
            else (255, 255, 255)
        )

        rect = piece_surface.get_rect(
            center=(
                x + SQUARE_SIZE // 2,
                y + SQUARE_SIZE // 2
            )
        )

        screen.blit(piece_surface, rect)


# ---------------- DRAW SELECTION ----------------

def draw_selection():
    if selected_square is not None:

        row = 7 - chess.square_rank(selected_square)
        col = chess.square_file(selected_square)

        x = col * SQUARE_SIZE
        y = row * SQUARE_SIZE

        pygame.draw.rect(
            screen,
            SELECT_COLOR,
            (x, y, SQUARE_SIZE, SQUARE_SIZE),
            5
        )

    for move in legal_moves:

        row = 7 - chess.square_rank(move.to_square)
        col = chess.square_file(move.to_square)

        x = col * SQUARE_SIZE
        y = row * SQUARE_SIZE

        pygame.draw.circle(
            screen,
            MOVE_COLOR,
            (
                x + SQUARE_SIZE // 2,
                y + SQUARE_SIZE // 2
            ),
            12
        )


# ---------------- DRAW INFO ----------------

def draw_info():
    pygame.draw.rect(
        screen,
        BACKGROUND,
        (0, BOARD_SIZE, WIDTH, HEIGHT - BOARD_SIZE)
    )

    if board.is_checkmate():

        if board.turn == chess.WHITE:
            message = "Black wins by checkmate!"
        else:
            message = "White wins by checkmate!"

    elif board.is_stalemate():
        message = "Draw - Stalemate"

    elif board.is_game_over():
        message = "Game over - Draw"

    elif ai_thinking:
        message = "AI is thinking..."

    elif board.turn == chess.WHITE:
        message = "Your turn - White"

    else:
        message = "AI turn - Black"

    text = info_font.render(
        message,
        True,
        TEXT_COLOR
    )

    screen.blit(text, (15, 610))

    stats_text = info_font.render(
        f"AI Nodes: {last_nodes} | Time: {last_time:.2f}s",
        True,
        TEXT_COLOR
    )

    screen.blit(stats_text, (15, 640))


# ---------------- PLAYER MOVE ----------------

def handle_player_click(pos):
    global selected_square, legal_moves

    if ai_thinking:
        return

    if board.turn != chess.WHITE:
        return

    if board.is_game_over():
        return

    x, y = pos

    if x >= BOARD_SIZE or y >= BOARD_SIZE:
        return

    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE

    square = chess.square(
        col,
        7 - row
    )

    clicked_piece = board.piece_at(square)

    # White fiqur seçmək
    if clicked_piece is not None and clicked_piece.color == chess.WHITE:

        selected_square = square

        legal_moves = [
            move
            for move in board.legal_moves
            if move.from_square == square
        ]

        return

    # Seçilmiş fiqurun gedişini etmək
    if selected_square is not None:

        move = chess.Move(
            selected_square,
            square
        )

        # Piyada son sıraya çatarsa, vəzirə çevrilir
        if (
            board.piece_at(selected_square).piece_type == chess.PAWN
            and chess.square_rank(square) in [0, 7]
        ):
            move = chess.Move(
                selected_square,
                square,
                promotion=chess.QUEEN
            )

        if move in board.legal_moves:

            board.push(move)

            selected_square = None
            legal_moves = []

            if not board.is_game_over():
                start_ai()

        else:

            # Başqa ağ fiqur seçmək imkanı
            if clicked_piece is not None and clicked_piece.color == chess.WHITE:

                selected_square = square

                legal_moves = [
                    move
                    for move in board.legal_moves
                    if move.from_square == square
                ]

            else:
                selected_square = None
                legal_moves = []
def restart_game():
    global board
    global selected_square
    global legal_moves
    global ai_thinking
    global last_nodes
    global last_time

    board = chess.Board()

    selected_square = None
    legal_moves = []

    ai_thinking = False
    last_nodes = 0
    last_time = 0.0

# ---------------- MAIN LOOP ----------------

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                handle_player_click(event.pos)

    # AI nəticəsini yoxlayırıq
    if not ai_queue.empty():

        result = ai_queue.get()

        ai_move, nodes_count, elapsed_time = result

        ai_thinking = False

        last_nodes = nodes_count
        last_time = elapsed_time

        if ai_move is not None and ai_move in board.legal_moves:
            board.push(ai_move)

    # Ekranı yeniləyirik
    screen.fill(BACKGROUND)

    draw_board()
    draw_selection()
    draw_pieces()
    draw_info()

    pygame.display.flip()


pygame.quit()
