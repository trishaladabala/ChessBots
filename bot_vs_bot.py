#!/usr/bin/env python3
"""
Bot vs Bot Chess GUI - Watch two chess engines play against each other
"""

import pygame
import chess
import sys
import os
from ChessEngine import MinimaxEngine, RandomEngine, GreedyEngine

# ---------- Configuration ----------
BOARD_SIZE = 640
PANEL_WIDTH = 350
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
pygame.display.set_caption("Chess Bot Battle Arena")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)
big_font = pygame.font.SysFont(None, 28)
title_font = pygame.font.SysFont(None, 32)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (230, 230, 230)
DARK_GRAY = (180, 180, 180)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
LIGHT_BLUE = (100, 150, 250)

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

# ---------- Engine options ----------
ENGINE_OPTIONS = [
    ("Random", lambda: RandomEngine()),
    ("Greedy", lambda: GreedyEngine()),
    ("Minimax D2", lambda: MinimaxEngine(depth=2)),
    ("Minimax D3", lambda: MinimaxEngine(depth=3)),
    ("Minimax D4", lambda: MinimaxEngine(depth=4)),
]

# ---------- Utilities ----------
def square_to_screen(square):
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    row = 7 - rank
    col = file
    x = col * SQ_SIZE
    y = row * SQ_SIZE
    return x, y

def draw_board(board, last_move=None):
    """Draw the chess board and pieces."""
    colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
    for r in range(8):
        for c in range(8):
            rect = pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            color = colors[(r+c) % 2]
            pygame.draw.rect(screen, color, rect)
    
    # Highlight last move
    if last_move:
        for sq in [last_move.from_square, last_move.to_square]:
            x, y = square_to_screen(sq)
            highlight = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
            highlight.fill((255, 255, 100, 100))
            screen.blit(highlight, (x, y))
    
    # Draw pieces
    for square, piece in board.piece_map().items():
        key = PIECE_KEYS[piece.symbol()]
        img = IMAGES[key]
        x, y = square_to_screen(square)
        screen.blit(img, (x, y))

def draw_button(x, y, w, h, text, color, hover=False):
    """Draw a button and return if it's hovered."""
    mouse_pos = pygame.mouse.get_pos()
    is_hover = (x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h)
    
    button_color = LIGHT_BLUE if is_hover else color
    pygame.draw.rect(screen, button_color, (x, y, w, h))
    pygame.draw.rect(screen, BLACK, (x, y, w, h), 2)
    
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + w//2, y + h//2))
    screen.blit(text_surf, text_rect)
    
    return is_hover

def draw_selector(x, y, w, h, options, selected_idx, label):
    """Draw engine selector with prev/next buttons."""
    # Label
    label_surf = font.render(label, True, BLACK)
    screen.blit(label_surf, (x, y - 25))
    
    # Previous button
    prev_hover = draw_button(x, y, 30, h, "<", DARK_GRAY)
    
    # Current selection display
    pygame.draw.rect(screen, WHITE, (x + 35, y, w - 70, h))
    pygame.draw.rect(screen, BLACK, (x + 35, y, w - 70, h), 2)
    text = options[selected_idx][0]
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + w//2, y + h//2))
    screen.blit(text_surf, text_rect)
    
    # Next button
    next_hover = draw_button(x + w - 30, y, 30, h, ">", DARK_GRAY)
    
    return prev_hover, next_hover

def update_move_history(board):
    """Convert move stack to SAN notation."""
    san_list = []
    tmp_board = chess.Board()
    for mv in board.move_stack:
        san_list.append(tmp_board.san(mv))
        tmp_board.push(mv)
    return san_list


def draw_panel(board, white_engine_name, black_engine_name, move_history, 
               game_running, game_over, speed_delay):
    """Draw the control panel."""
    panel_x = BOARD_SIZE
    panel_rect = pygame.Rect(panel_x, 0, PANEL_WIDTH, HEIGHT)
    pygame.draw.rect(screen, GRAY, panel_rect)
    
    y_offset = 10
    
    # Title
    title = title_font.render("Bot Battle Arena", True, BLUE)
    screen.blit(title, (panel_x + 10, y_offset))
    y_offset += 40
    
    # Engine info
    white_text = font.render(f"White: {white_engine_name}", True, BLACK)
    screen.blit(white_text, (panel_x + 10, y_offset))
    y_offset += 25
    
    black_text = font.render(f"Black: {black_engine_name}", True, BLACK)
    screen.blit(black_text, (panel_x + 10, y_offset))
    y_offset += 35
    
    # Game status
    if game_over:
        result = board.result()
        status_text = f"Game Over: {result}"
        status_color = RED
    elif game_running:
        turn = "White" if board.turn == chess.WHITE else "Black"
        status_text = f"{turn} to move..."
        status_color = GREEN
    else:
        status_text = "Ready to start"
        status_color = BLUE
    
    status_surf = big_font.render(status_text, True, status_color)
    screen.blit(status_surf, (panel_x + 10, y_offset))
    y_offset += 40
    
    # Move count
    move_count = font.render(f"Move: {board.fullmove_number}", True, BLACK)
    screen.blit(move_count, (panel_x + 10, y_offset))
    y_offset += 25
    
    # Speed
    speed_text = font.render(f"Speed: {1000/speed_delay:.1f} moves/sec", True, BLACK)
    screen.blit(speed_text, (panel_x + 10, y_offset))
    y_offset += 35
    
    # Controls hint
    pygame.draw.line(screen, BLACK, (panel_x + 10, y_offset), (panel_x + PANEL_WIDTH - 10, y_offset), 1)
    y_offset += 15
    
    controls = [
        "SPACE - Pause/Resume",
        "R - Reset game",
        "+ - Speed up",
        "- - Slow down",
        "Q - Quit",
    ]
    
    for control in controls:
        ctrl_surf = font.render(control, True, BLACK)
        screen.blit(ctrl_surf, (panel_x + 10, y_offset))
        y_offset += 20
    
    y_offset += 10
    pygame.draw.line(screen, BLACK, (panel_x + 10, y_offset), (panel_x + PANEL_WIDTH - 10, y_offset), 1)
    y_offset += 15
    
    # Move history
    history_title = big_font.render("Move History:", True, BLACK)
    screen.blit(history_title, (panel_x + 10, y_offset))
    y_offset += 30
    
    # Display last 15 moves
    rows = []
    for i in range(0, len(move_history), 2):
        white_move = move_history[i] if i < len(move_history) else ""
        black_move = move_history[i+1] if (i+1) < len(move_history) else ""
        move_num = (i//2) + 1
        rows.append(f"{move_num}. {white_move:8s} {black_move}")
    
    # Show last 15 moves
    rows = rows[-15:]
    for row in rows:
        if y_offset > HEIGHT - 25:
            break
        row_surf = font.render(row, True, BLACK)
        screen.blit(row_surf, (panel_x + 10, y_offset))
        y_offset += 18

# ---------- Main ----------
def main():
    # Game state
    board = chess.Board()
    move_history = []
    last_move = None
    
    # Engine selection
    white_idx = 4  # Default: Minimax D4
    black_idx = 2  # Default: Minimax D2
    
    white_engine = None
    black_engine = None
    
    # Game control
    game_running = False
    game_over = False
    speed_delay = 1000  # milliseconds between moves
    last_move_time = 0
    paused = False
    
    # UI state
    setup_mode = True
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if not setup_mode:
                        paused = not paused
                elif event.key == pygame.K_r:
                    # Reset
                    board = chess.Board()
                    move_history = []
                    last_move = None
                    game_running = False
                    game_over = False
                    setup_mode = True
                    paused = False
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    speed_delay = max(100, speed_delay - 200)
                elif event.key == pygame.K_MINUS:
                    speed_delay = min(5000, speed_delay + 200)
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                
                # Only handle panel clicks
                if mouse_x >= BOARD_SIZE:
                    if setup_mode:
                        # Check selector buttons
                        # White engine selector (y=100)
                        white_x, white_y = BOARD_SIZE + 20, 100
                        if white_y <= mouse_y <= white_y + 35:
                            if white_x <= mouse_x <= white_x + 30:  # Prev
                                white_idx = (white_idx - 1) % len(ENGINE_OPTIONS)
                            elif white_x + 280 <= mouse_x <= white_x + 310:  # Next
                                white_idx = (white_idx + 1) % len(ENGINE_OPTIONS)
                        
                        # Black engine selector (y=160)
                        black_x, black_y = BOARD_SIZE + 20, 160
                        if black_y <= mouse_y <= black_y + 35:
                            if black_x <= mouse_x <= black_x + 30:  # Prev
                                black_idx = (black_idx - 1) % len(ENGINE_OPTIONS)
                            elif black_x + 280 <= mouse_x <= black_x + 310:  # Next
                                black_idx = (black_idx + 1) % len(ENGINE_OPTIONS)
                        
                        # Start button (y=220)
                        start_x, start_y = BOARD_SIZE + 70, 220
                        if start_x <= mouse_x <= start_x + 200 and start_y <= mouse_y <= start_y + 50:
                            # Start the game
                            white_engine = ENGINE_OPTIONS[white_idx][1]()
                            black_engine = ENGINE_OPTIONS[black_idx][1]()
                            setup_mode = False
                            game_running = True
                            last_move_time = current_time
        
        # Game logic
        if not setup_mode and game_running and not paused and not game_over:
            # Check if it's time for next move
            if current_time - last_move_time >= speed_delay:
                if not board.is_game_over():
                    # Get move from appropriate engine
                    engine = white_engine if board.turn == chess.WHITE else black_engine
                    move = engine.get_move(board)
                    
                    if move and move in board.legal_moves:
                        board.push(move)
                        last_move = move
                        move_history = update_move_history(board)
                        last_move_time = current_time
                    else:
                        game_over = True
                else:
                    game_over = True
                    game_running = False
        
        # Drawing
        screen.fill(WHITE)
        
        if setup_mode:
            # Draw board
            draw_board(board)
            
            # Draw setup panel
            panel_x = BOARD_SIZE
            pygame.draw.rect(screen, GRAY, (panel_x, 0, PANEL_WIDTH, HEIGHT))
            
            # Title
            title = title_font.render("Bot Battle Setup", True, BLUE)
            screen.blit(title, (panel_x + 30, 20))
            
            # Instructions
            inst = font.render("Select engines and press START", True, BLACK)
            screen.blit(inst, (panel_x + 20, 60))
            
            # White engine selector
            draw_selector(panel_x + 20, 100, 310, 35, ENGINE_OPTIONS, white_idx, "White Engine:")
            
            # Black engine selector
            draw_selector(panel_x + 20, 160, 310, 35, ENGINE_OPTIONS, black_idx, "Black Engine:")
            
            # Start button
            draw_button(panel_x + 70, 220, 200, 50, "START BATTLE", GREEN)
            
            # Info
            info_y = 300
            info_lines = [
                "",
                "Controls:",
                "SPACE - Pause/Resume",
                "R - Reset",
                "+/- - Speed control",
                "Q - Quit",
            ]
            for line in info_lines:
                info_surf = font.render(line, True, BLACK)
                screen.blit(info_surf, (panel_x + 20, info_y))
                info_y += 25
        else:
            # Draw game
            draw_board(board, last_move)
            white_name = ENGINE_OPTIONS[white_idx][0]
            black_name = ENGINE_OPTIONS[black_idx][0]
            draw_panel(board, white_name, black_name, move_history, 
                      game_running and not paused, game_over, speed_delay)
            
            # Draw pause overlay if paused
            if paused:
                overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                
                pause_text = title_font.render("PAUSED", True, WHITE)
                pause_rect = pause_text.get_rect(center=(BOARD_SIZE//2, BOARD_SIZE//2))
                screen.blit(pause_text, pause_rect)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
