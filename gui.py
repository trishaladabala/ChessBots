import pygame
import chess
import sys
import os
import random
from ChessEngine import MinimaxEngine, RandomEngine, GreedyEngine

# ---------- Configuration ----------
BOARD_SIZE = 640
PANEL_WIDTH = 300
WIDTH = BOARD_SIZE + PANEL_WIDTH
HEIGHT = BOARD_SIZE
SQ_SIZE = BOARD_SIZE // 8
FPS = 30

IMAGE_DIR = "pieces-basic-png"
PIECE_KEYS = {
    "P": "wp", "R": "wr", "N": "wn", "B": "wb", "Q": "wq", "K": "wk",
    "p": "bp", "r": "br", "n": "bn", "b": "bb", "q": "bq", "k": "bk",
}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Engine GUI")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)
big_font = pygame.font.SysFont(None, 28)

# ---------- Load piece images ----------
def load_images():
    images = {}
    for key in PIECE_KEYS.values():
        path = os.path.join(IMAGE_DIR, f"{key}.png")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing piece image: {path}")
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (SQ_SIZE, SQ_SIZE))
        images[key] = img
    return images

IMAGES = load_images()

# ---------- Utilities ----------
def square_to_screen(square):
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    row = 7 - rank
    col = file
    x = col * SQ_SIZE
    y = row * SQ_SIZE
    return x, y

def screen_to_square(x, y):
    col = x // SQ_SIZE
    row = y // SQ_SIZE
    rank = 7 - int(row)
    file = int(col)
    if 0 <= file <= 7 and 0 <= rank <= 7:
        return chess.square(file, rank)
    return None

def draw_board(board, selected_sq, legal_targets):
    colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
    for r in range(8):
        for c in range(8):
            rect = pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            color = colors[(r+c) % 2]
            pygame.draw.rect(screen, color, rect)

    if selected_sq is not None:
        x, y = square_to_screen(selected_sq)
        highlight = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
        highlight.fill((255, 255, 0, 80))
        screen.blit(highlight, (x, y))

    for t in legal_targets:
        x, y = square_to_screen(t)
        highlight = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
        highlight.fill((0, 255, 0, 80))
        screen.blit(highlight, (x, y))

    # draw pieces
    for square, piece in board.piece_map().items():
        key = PIECE_KEYS[piece.symbol()]
        img = IMAGES[key]
        x, y = square_to_screen(square)
        screen.blit(img, (x, y))

def draw_panel(board, engine_name, minimax_depth, human_color, move_history):
    panel_x = BOARD_SIZE
    panel_rect = pygame.Rect(panel_x, 0, PANEL_WIDTH, HEIGHT)
    pygame.draw.rect(screen, pygame.Color(230, 230, 230), panel_rect)

    header = big_font.render("Chess Engine UI", True, (10, 10, 10))
    screen.blit(header, (panel_x + 10, 8))

    engine_text = font.render(f"Engine: {engine_name}", True, (10, 10, 10))
    screen.blit(engine_text, (panel_x + 10, 40))
    depth_text = font.render(f"Minimax depth: {minimax_depth}", True, (10, 10, 10))
    screen.blit(depth_text, (panel_x + 10, 60))
    human_text = font.render(f"Human side: {'White' if human_color == chess.WHITE else 'Black'} (press T to toggle)", True, (10, 10, 10))
    screen.blit(human_text, (panel_x + 10, 80))

    controls = [
        "Controls:",
        "1 - Minimax engine",
        "2 - Random engine",
        "3 - Greedy engine",
        "+ / - : change Minimax depth",
        "U - Undo last ply(s)",
        "T - Toggle human side",
        "Q - Quit"
    ]
    y = 110
    for line in controls:
        screen.blit(font.render(line, True, (10,10,10)), (panel_x + 10, y))
        y += 20

    screen.blit(big_font.render("Move history:", True, (10, 10, 10)), (panel_x + 10, 260))
    history_y = 290

    rows = []
    for i in range(0, len(move_history), 2):
        white_move = move_history[i] if i < len(move_history) else ""
        black_move = move_history[i+1] if (i+1) < len(move_history) else ""
        move_num = (i//2) + 1
        rows.append(f"{move_num}. {white_move}   {black_move}")
    rows = rows[-12:]
    for r in rows:
        screen.blit(font.render(r, True, (10,10,10)), (panel_x + 10, history_y))
        history_y += 18

# ---------- Game + Engine setup ----------
board = chess.Board()
engine = MinimaxEngine(depth=2)
engine_name = "Minimax"
minimax_depth = 2
human_side = chess.WHITE

selected_square = None
legal_targets = []
move_history = []

def update_move_history(board):
    san_list = []
    tmp_board = chess.Board()
    for mv in board.move_stack:
        san_list.append(tmp_board.san(mv))
        tmp_board.push(mv)
    return san_list

# ---------- Main loop ----------
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            # ignore clicks in panel
            if x >= BOARD_SIZE:
                continue
            sq = screen_to_square(x, y)
            if sq is None:
                continue

            # Only allow selecting/clicking when it's the human's turn
            if board.turn != human_side:
                # not human's turn — ignore clicks on board
                continue

            # If nothing selected yet, select if there's a piece of the human's color
            if selected_square is None:
                piece = board.piece_at(sq)
                if piece and piece.color == human_side:
                    selected_square = sq
                    legal_targets = [mv.to_square for mv in board.legal_moves if mv.from_square == sq]
                else:
                    # ignore clicks on empty or opponent pieces
                    pass
            else:
                # Attempt move from selected_square to clicked sq
                mv = chess.Move(selected_square, sq)
                # handle promotions automatically to queen
                piece_at_from = board.piece_at(selected_square)
                if piece_at_from and piece_at_from.piece_type == chess.PAWN:
                    to_rank = chess.square_rank(sq)
                    if (piece_at_from.color == chess.WHITE and to_rank == 7) or \
                       (piece_at_from.color == chess.BLACK and to_rank == 0):
                        mv.promotion = chess.QUEEN

                # If the move is legal, push it
                if mv in board.legal_moves:
                    board.push(mv)
                    move_history = update_move_history(board)
                    selected_square = None
                    legal_targets = []
                    # do NOT make the engine move here; auto-play section will handle engine move
                else:
                    # Reselect if clicking another own piece
                    piece = board.piece_at(sq)
                    if piece and piece.color == human_side:
                        selected_square = sq
                        legal_targets = [mv.to_square for mv in board.legal_moves if mv.from_square == sq]
                    else:
                        # invalid target, deselect
                        selected_square = None
                        legal_targets = []

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_1:
                engine = MinimaxEngine(depth=minimax_depth)
                engine_name = "Minimax"
            elif event.key == pygame.K_2:
                engine = RandomEngine()
                engine_name = "Random"
            elif event.key == pygame.K_3:
                engine = GreedyEngine()
                engine_name = "Greedy"
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                minimax_depth += 1
                if engine_name == "Minimax":
                    engine = MinimaxEngine(depth=minimax_depth)
            elif event.key == pygame.K_MINUS:
                minimax_depth = max(1, minimax_depth - 1)
                if engine_name == "Minimax":
                    engine = MinimaxEngine(depth=minimax_depth)
            elif event.key == pygame.K_t:
                human_side = chess.BLACK if human_side == chess.WHITE else chess.WHITE
                selected_square = None
                legal_targets = []
            elif event.key == pygame.K_u:
                # Undo behaviour: pop one ply; if it's still not human's turn, pop another (so human gets the move)
                if len(board.move_stack) > 0:
                    board.pop()
                if board.turn != human_side and len(board.move_stack) > 0:
                    board.pop()
                move_history = update_move_history(board)
                selected_square = None
                legal_targets = []

    # If it's engine's turn and engine is controlling that color, let it move (auto-play)
    if not board.is_game_over() and board.turn != human_side:
        eng_move = engine.get_move(board)
        if eng_move is not None and eng_move in board.legal_moves:
            board.push(eng_move)
            move_history = update_move_history(board)

    # draw UI
    draw_board(board, selected_square, legal_targets)
    draw_panel(board, engine_name, minimax_depth, human_side, move_history)

    if board.is_game_over():
        result_text = "Game over: " + board.result()
        screen.blit(big_font.render(result_text, True, (200,10,10)), (10, BOARD_SIZE - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()
