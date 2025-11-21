#!/usr/bin/env python3
"""
Minichess Bot vs Bot GUI - Watch two chess engines play Minichess variants
Supports 4x4 and 4x5 Silverman Minichess
"""

import pygame
import sys
import os
from MinichessEngine import (
    MinichessBoard, MinimaxEngine, RandomEngine, GreedyEngine,
    Color, PieceType, Piece
)

# ---------- Configuration ----------
BOARD_SIZE = 640
PANEL_WIDTH = 350
WIDTH = BOARD_SIZE + PANEL_WIDTH
HEIGHT = BOARD_SIZE
FPS = 30

IMAGE_DIR = "pieces-basic-png"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minichess Bot Battle Arena")
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
YELLOW = (255, 255, 100)

# ---------- Piece image mapping ----------
PIECE_IMAGE_MAP = {
    (PieceType.PAWN, Color.WHITE): "wp",
    (PieceType.ROOK, Color.WHITE): "wr",
    (PieceType.BISHOP, Color.WHITE): "wb",
    (PieceType.KNIGHT, Color.WHITE): "wn",
    (PieceType.QUEEN, Color.WHITE): "wq",
    (PieceType.KING, Color.WHITE): "wk",
    (PieceType.PAWN, Color.BLACK): "bp",
    (PieceType.ROOK, Color.BLACK): "br",
    (PieceType.BISHOP, Color.BLACK): "bb",
    (PieceType.KNIGHT, Color.BLACK): "bn",
    (PieceType.QUEEN, Color.BLACK): "bq",
    (PieceType.KING, Color.BLACK): "bk",
}

# ---------- Load piece images ----------
def load_images(sq_size):
    images = {}
    for (ptype, color), key in PIECE_IMAGE_MAP.items():
        path = os.path.join(IMAGE_DIR, f"{key}.png")
        if not os.path.exists(path):
            print(f"Warning: Missing piece image: {path}")
            continue
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (sq_size, sq_size))
        images[(ptype, color)] = img
    return images

# ---------- Engine options ----------
ENGINE_OPTIONS = [
    ("Random", lambda: RandomEngine()),
    ("Greedy", lambda: GreedyEngine()),
    ("Minimax D2", lambda: MinimaxEngine(depth=2)),
    ("Minimax D3", lambda: MinimaxEngine(depth=3)),
    ("Minimax D4", lambda: MinimaxEngine(depth=4)),
    ("Minimax D5", lambda: MinimaxEngine(depth=5)),
]

VARIANT_OPTIONS = ["4x4", "4x5", "4x8", "5x5", "5x6", "6x6"]

# ---------- Utilities ----------
def get_board_size(variant):
    """Get board dimensions for a variant."""
    if variant == '4x4':
        return (4, 4)
    elif variant == '4x5':
        return (5, 4)
    elif variant == '4x8':
        return (8, 4)
    elif variant == '5x5':
        return (5, 5)
    elif variant == '5x6':
        return (6, 5)
    elif variant == '6x6':
        return (6, 6)
    return (5, 4)  # Default

def draw_board(board, sq_size, last_move=None):
    """Draw the Minichess board and pieces."""
    colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
    
    # Calculate offset to center the board
    board_width = board.cols * sq_size
    board_height = board.rows * sq_size
    offset_x = (BOARD_SIZE - board_width) // 2
    offset_y = (BOARD_SIZE - board_height) // 2
    
    for r in range(board.rows):
        for c in range(board.cols):
            rect = pygame.Rect(
                offset_x + c * sq_size,
                offset_y + (board.rows - 1 - r) * sq_size,
                sq_size, sq_size
            )
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, rect)
    
    # Highlight last move
    if last_move:
        from_row, from_col = last_move.from_pos
        to_row, to_col = last_move.to_pos
        
        for (row, col) in [(from_row, from_col), (to_row, to_col)]:
            x = offset_x + col * sq_size
            y = offset_y + (board.rows - 1 - row) * sq_size
            highlight = pygame.Surface((sq_size, sq_size), pygame.SRCALPHA)
            highlight.fill((255, 255, 100, 100))
            screen.blit(highlight, (x, y))
    
    # Draw pieces
    for row in range(board.rows):
        for col in range(board.cols):
            piece = board.board[row][col]
            if piece:
                key = (piece.type, piece.color)
                if key in IMAGES:
                    img = IMAGES[key]
                    x = offset_x + col * sq_size
                    y = offset_y + (board.rows - 1 - row) * sq_size
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
    """Draw selector with prev/next buttons."""
    # Label
    label_surf = font.render(label, True, BLACK)
    screen.blit(label_surf, (x, y - 25))
    
    # Previous button
    prev_hover = draw_button(x, y, 30, h, "<", DARK_GRAY)
    
    # Current selection display
    pygame.draw.rect(screen, WHITE, (x + 35, y, w - 70, h))
    pygame.draw.rect(screen, BLACK, (x + 35, y, w - 70, h), 2)
    
    if isinstance(options[selected_idx], tuple):
        text = options[selected_idx][0]
    else:
        text = options[selected_idx]
    
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + w//2, y + h//2))
    screen.blit(text_surf, text_rect)
    
    # Next button
    next_hover = draw_button(x + w - 30, y, 30, h, ">", DARK_GRAY)
    
    return prev_hover, next_hover

def draw_panel(board, variant, white_engine_name, black_engine_name, move_history,
               game_running, game_over, speed_delay):
    """Draw the control panel."""
    panel_x = BOARD_SIZE
    panel_rect = pygame.Rect(panel_x, 0, PANEL_WIDTH, HEIGHT)
    pygame.draw.rect(screen, GRAY, panel_rect)
    
    y_offset = 10
    
    # Title
    title = title_font.render("Minichess Battle", True, BLUE)
    screen.blit(title, (panel_x + 10, y_offset))
    y_offset += 35
    
    # Variant
    variant_text = font.render(f"Variant: {variant}", True, BLACK)
    screen.blit(variant_text, (panel_x + 10, y_offset))
    y_offset += 30
    
    # Engine info
    white_text = font.render(f"White: {white_engine_name}", True, BLACK)
    screen.blit(white_text, (panel_x + 10, y_offset))
    y_offset += 25
    
    black_text = font.render(f"Black: {black_engine_name}", True, BLACK)
    screen.blit(black_text, (panel_x + 10, y_offset))
    y_offset += 35
    
    # Game status
    if game_over:
        result = board.get_result()
        status_text = f"Game Over: {result}"
        status_color = RED
    elif game_running:
        turn = "White" if board.turn == Color.WHITE else "Black"
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
    
    # Display last 20 moves
    display_moves = move_history[-20:]
    for i, move_str in enumerate(display_moves):
        if y_offset > HEIGHT - 25:
            break
        move_surf = font.render(f"{i + len(move_history) - len(display_moves) + 1}. {move_str}", True, BLACK)
        screen.blit(move_surf, (panel_x + 10, y_offset))
        y_offset += 18

# ---------- Main ----------
def main():
    global IMAGES
    
    # Game state
    variant_idx = 1  # Default to 4x5
    variant = VARIANT_OPTIONS[variant_idx]
    
    # Calculate square size based on variant
    rows, cols = get_board_size(variant)
    SQ_SIZE = BOARD_SIZE // max(rows, cols)
    
    # Load images with appropriate size
    IMAGES = load_images(SQ_SIZE)
    
    board = MinichessBoard(variant)
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
                    board = MinichessBoard(variant)
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
                        # Variant selector (y=100)
                        variant_x, variant_y = BOARD_SIZE + 20, 100
                        if variant_y <= mouse_y <= variant_y + 35:
                            if variant_x <= mouse_x <= variant_x + 30:  # Prev
                                variant_idx = (variant_idx - 1) % len(VARIANT_OPTIONS)
                                variant = VARIANT_OPTIONS[variant_idx]
                                board = MinichessBoard(variant)
                                rows = 4 if variant == '4x4' else 5
                                SQ_SIZE = BOARD_SIZE // max(rows, 4)
                                IMAGES = load_images(SQ_SIZE)
                            elif variant_x + 280 <= mouse_x <= variant_x + 310:  # Next
                                variant_idx = (variant_idx + 1) % len(VARIANT_OPTIONS)
                                variant = VARIANT_OPTIONS[variant_idx]
                                board = MinichessBoard(variant)
                                rows = 4 if variant == '4x4' else 5
                                SQ_SIZE = BOARD_SIZE // max(rows, 4)
                                IMAGES = load_images(SQ_SIZE)
                        
                        # White engine selector (y=160)
                        white_x, white_y = BOARD_SIZE + 20, 160
                        if white_y <= mouse_y <= white_y + 35:
                            if white_x <= mouse_x <= white_x + 30:  # Prev
                                white_idx = (white_idx - 1) % len(ENGINE_OPTIONS)
                            elif white_x + 280 <= mouse_x <= white_x + 310:  # Next
                                white_idx = (white_idx + 1) % len(ENGINE_OPTIONS)
                        
                        # Black engine selector (y=220)
                        black_x, black_y = BOARD_SIZE + 20, 220
                        if black_y <= mouse_y <= black_y + 35:
                            if black_x <= mouse_x <= black_x + 30:  # Prev
                                black_idx = (black_idx - 1) % len(ENGINE_OPTIONS)
                            elif black_x + 280 <= mouse_x <= black_x + 310:  # Next
                                black_idx = (black_idx + 1) % len(ENGINE_OPTIONS)
                        
                        # Start button (y=280)
                        start_x, start_y = BOARD_SIZE + 70, 280
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
                    engine = white_engine if board.turn == Color.WHITE else black_engine
                    move = engine.get_move(board)
                    
                    if move:
                        board.make_move(move)
                        last_move = move
                        move_history.append(str(move))
                        last_move_time = current_time
                    else:
                        game_over = True
                else:
                    game_over = True
                    game_running = False
        
        # Drawing
        screen.fill(WHITE)
        
        # Calculate square size for current variant
        rows, cols = get_board_size(variant)
        SQ_SIZE = BOARD_SIZE // max(rows, cols)
        
        if setup_mode:
            # Draw empty board
            temp_board = MinichessBoard(variant)
            draw_board(temp_board, SQ_SIZE)
            
            # Draw setup panel
            panel_x = BOARD_SIZE
            pygame.draw.rect(screen, GRAY, (panel_x, 0, PANEL_WIDTH, HEIGHT))
            
            # Title
            title = title_font.render("Minichess Setup", True, BLUE)
            screen.blit(title, (panel_x + 30, 20))
            
            # Instructions
            inst = font.render("Select variant, engines, and START", True, BLACK)
            screen.blit(inst, (panel_x + 15, 60))
            
            # Variant selector
            draw_selector(panel_x + 20, 100, 310, 35, VARIANT_OPTIONS, variant_idx, "Board Variant:")
            
            # White engine selector
            draw_selector(panel_x + 20, 160, 310, 35, ENGINE_OPTIONS, white_idx, "White Engine:")
            
            # Black engine selector
            draw_selector(panel_x + 20, 220, 310, 35, ENGINE_OPTIONS, black_idx, "Black Engine:")
            
            # Start button
            draw_button(panel_x + 70, 280, 200, 50, "START BATTLE", GREEN)
            
            # Info
            info_y = 360
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
            draw_board(board, SQ_SIZE, last_move)
            white_name = ENGINE_OPTIONS[white_idx][0]
            black_name = ENGINE_OPTIONS[black_idx][0]
            draw_panel(board, variant, white_name, black_name, move_history,
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
