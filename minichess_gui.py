#!/usr/bin/env python3
"""
Minichess GUI - Play Minichess against AI or Human
Supports 4x4 and 4x5 Silverman variants
"""

import pygame
import sys
import os
from MinichessEngine import (
    MinichessBoard, MinimaxEngine, RandomEngine, GreedyEngine,
    Color, PieceType, Move
)

# ---------- Configuration ----------
BOARD_SIZE = 640
PANEL_WIDTH = 350
WIDTH = BOARD_SIZE + PANEL_WIDTH
HEIGHT = BOARD_SIZE
FPS = 60

IMAGE_DIR = "pieces-basic-png"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minichess - Play Against AI")
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
HIGHLIGHT_GREEN = (100, 200, 100, 128)
HIGHLIGHT_BLUE = (100, 150, 200, 128)

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

# ---------- Game Mode Options ----------
ENGINE_OPTIONS = [
    ("Human vs Human", None),
    ("Random", RandomEngine()),
    ("Greedy", GreedyEngine()),
    ("Minimax D2", MinimaxEngine(depth=2)),
    ("Minimax D3", MinimaxEngine(depth=3)),
    ("Minimax D4", MinimaxEngine(depth=4)),
    ("Minimax D5", MinimaxEngine(depth=5)),
]

VARIANT_OPTIONS = ["4x4", "4x5", "4x8", "5x5", "5x6", "6x6"]
COLOR_OPTIONS = ["White", "Black"]

# ---------- Utilities ----------
def screen_to_square(x, y, board, sq_size):
    """Convert screen coordinates to board position."""
    if x >= BOARD_SIZE:
        return None
    
    # Calculate offset to center the board
    board_width = board.cols * sq_size
    board_height = board.rows * sq_size
    offset_x = (BOARD_SIZE - board_width) // 2
    offset_y = (BOARD_SIZE - board_height) // 2
    
    # Adjust for offset
    x -= offset_x
    y -= offset_y
    
    if x < 0 or y < 0:
        return None
    
    col = x // sq_size
    row = board.rows - 1 - (y // sq_size)
    
    if 0 <= row < board.rows and 0 <= col < board.cols:
        return (row, col)
    return None

def square_to_screen(row, col, board, sq_size):
    """Convert board position to screen coordinates."""
    # Calculate offset to center the board
    board_width = board.cols * sq_size
    board_height = board.rows * sq_size
    offset_x = (BOARD_SIZE - board_width) // 2
    offset_y = (BOARD_SIZE - board_height) // 2
    
    x = offset_x + col * sq_size
    y = offset_y + (board.rows - 1 - row) * sq_size
    return (x, y)

def draw_board(board, sq_size, selected_square=None, legal_moves=None, last_move=None):
    """Draw the Minichess board and pieces."""
    colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]
    
    # Calculate offset to center the board
    board_width = board.cols * sq_size
    board_height = board.rows * sq_size
    offset_x = (BOARD_SIZE - board_width) // 2
    offset_y = (BOARD_SIZE - board_height) // 2
    
    # Draw squares
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
            x, y = square_to_screen(row, col, board, sq_size)
            highlight = pygame.Surface((sq_size, sq_size), pygame.SRCALPHA)
            highlight.fill((255, 255, 100, 100))
            screen.blit(highlight, (x, y))
    
    # Highlight selected square
    if selected_square:
        row, col = selected_square
        x, y = square_to_screen(row, col, board, sq_size)
        highlight = pygame.Surface((sq_size, sq_size), pygame.SRCALPHA)
        highlight.fill(HIGHLIGHT_BLUE)
        screen.blit(highlight, (x, y))
    
    # Highlight legal move destinations
    if legal_moves:
        for move in legal_moves:
            to_row, to_col = move.to_pos
            x, y = square_to_screen(to_row, to_col, board, sq_size)
            
            # Draw a circle for legal moves
            center_x = x + sq_size // 2
            center_y = y + sq_size // 2
            
            if move.captured:
                # Draw ring for captures
                pygame.draw.circle(screen, (200, 50, 50, 180), (center_x, center_y), sq_size // 3, 5)
            else:
                # Draw dot for normal moves
                pygame.draw.circle(screen, (100, 200, 100, 180), (center_x, center_y), sq_size // 6)
    
    # Draw pieces
    for row in range(board.rows):
        for col in range(board.cols):
            piece = board.board[row][col]
            if piece:
                key = (piece.type, piece.color)
                if key in IMAGES:
                    img = IMAGES[key]
                    x, y = square_to_screen(row, col, board, sq_size)
                    screen.blit(img, (x, y))

def draw_button(x, y, w, h, text, color):
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
    
    # Truncate long text
    if len(text) > 22:
        text = text[:19] + "..."
    
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + w//2, y + h//2))
    screen.blit(text_surf, text_rect)
    
    # Next button
    next_hover = draw_button(x + w - 30, y, 30, h, ">", DARK_GRAY)
    
    return prev_hover, next_hover

def draw_panel(board, variant, mode_name, move_history, game_over):
    """Draw the control panel."""
    panel_x = BOARD_SIZE
    panel_rect = pygame.Rect(panel_x, 0, PANEL_WIDTH, HEIGHT)
    pygame.draw.rect(screen, GRAY, panel_rect)
    
    y_offset = 10
    
    # Title
    title = title_font.render("Minichess", True, BLUE)
    screen.blit(title, (panel_x + 10, y_offset))
    y_offset += 35
    
    # Variant
    variant_text = font.render(f"Variant: {variant}", True, BLACK)
    screen.blit(variant_text, (panel_x + 10, y_offset))
    y_offset += 25
    
    # Mode
    mode_text = font.render(f"Mode: {mode_name[:28]}", True, BLACK)
    screen.blit(mode_text, (panel_x + 10, y_offset))
    y_offset += 35
    
    # Game status
    if game_over:
        result = board.get_result()
        if result == "1-0":
            status_text = "White Wins!"
        elif result == "0-1":
            status_text = "Black Wins!"
        else:
            status_text = "Draw!"
        status_color = RED
    else:
        turn = "White" if board.turn == Color.WHITE else "Black"
        status_text = f"{turn} to move"
        status_color = GREEN
    
    status_surf = big_font.render(status_text, True, status_color)
    screen.blit(status_surf, (panel_x + 10, y_offset))
    y_offset += 40
    
    # Move count
    move_count = font.render(f"Move: {board.fullmove_number}", True, BLACK)
    screen.blit(move_count, (panel_x + 10, y_offset))
    y_offset += 35
    
    # Controls hint
    pygame.draw.line(screen, BLACK, (panel_x + 10, y_offset), (panel_x + PANEL_WIDTH - 10, y_offset), 1)
    y_offset += 15
    
    controls = [
        "Controls:",
        "Click - Select/Move",
        "R - Reset game",
        "U - Undo move",
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
        move_num = i + len(move_history) - len(display_moves) + 1
        move_surf = font.render(f"{move_num}. {move_str}", True, BLACK)
        screen.blit(move_surf, (panel_x + 10, y_offset))
        y_offset += 18

# ---------- Main ----------
def main():
    global IMAGES
    
    # Setup state
    variant_idx = 1  # Default to 4x5
    engine_idx = 4  # Default to Minimax D3
    color_idx = 0  # Default to White
    
    variant = VARIANT_OPTIONS[variant_idx]
    
    # Calculate square size based on variant
    def get_board_size(var):
        if var in ['4x4', '4x5']:
            return (4, 4) if var == '4x4' else (5, 4)
        elif var == '4x8':
            return (8, 4)
        elif var == '5x5':
            return (5, 5)
        elif var == '5x6':
            return (6, 5)
        elif var == '6x6':
            return (6, 6)
        return (5, 4)  # Default
    
    rows, cols = get_board_size(variant)
    SQ_SIZE = BOARD_SIZE // max(rows, cols)
    
    # Load images
    IMAGES = load_images(SQ_SIZE)
    
    # Game state
    board = None
    move_history = []
    last_move = None
    selected_square = None
    legal_moves_for_selected = []
    game_over = False
    
    # UI state
    setup_mode = True
    ai_thinking = False
    
    # Current game settings
    human_color = None
    ai_engine = None
    
    running = True
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset
                    board = None
                    move_history = []
                    last_move = None
                    selected_square = None
                    legal_moves_for_selected = []
                    game_over = False
                    setup_mode = True
                elif event.key == pygame.K_u and not setup_mode and not game_over:
                    # Undo move
                    if len(move_history) > 0:
                        # Reset to new board and replay all moves except last
                        board = MinichessBoard(variant)
                        moves_to_replay = move_history[:-1]
                        move_history = []
                        
                        # If playing against AI, undo 2 moves to get back to player's turn
                        if ai_engine and len(moves_to_replay) > 0:
                            moves_to_replay = moves_to_replay[:-1]
                        
                        # Replay moves
                        for move_str in moves_to_replay:
                            # Find the move that matches this string
                            legal = board.generate_legal_moves()
                            for mv in legal:
                                if str(mv) == move_str:
                                    board.make_move(mv)
                                    move_history.append(move_str)
                                    last_move = mv
                                    break
                        
                        selected_square = None
                        legal_moves_for_selected = []
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                
                if setup_mode:
                    # Handle setup clicks
                    if mouse_x >= BOARD_SIZE:
                        # Variant selector (y=100)
                        variant_x, variant_y = BOARD_SIZE + 20, 100
                        if variant_y <= mouse_y <= variant_y + 35:
                            if variant_x <= mouse_x <= variant_x + 30:  # Prev
                                variant_idx = (variant_idx - 1) % len(VARIANT_OPTIONS)
                                variant = VARIANT_OPTIONS[variant_idx]
                                rows, cols = get_board_size(variant)
                                SQ_SIZE = BOARD_SIZE // max(rows, cols)
                                IMAGES = load_images(SQ_SIZE)
                            elif variant_x + 280 <= mouse_x <= variant_x + 310:  # Next
                                variant_idx = (variant_idx + 1) % len(VARIANT_OPTIONS)
                                variant = VARIANT_OPTIONS[variant_idx]
                                rows, cols = get_board_size(variant)
                                SQ_SIZE = BOARD_SIZE // max(rows, cols)
                                IMAGES = load_images(SQ_SIZE)
                        
                        # Opponent engine selector (y=160)
                        engine_x, engine_y = BOARD_SIZE + 20, 160
                        if engine_y <= mouse_y <= engine_y + 35:
                            if engine_x <= mouse_x <= engine_x + 30:  # Prev
                                engine_idx = (engine_idx - 1) % len(ENGINE_OPTIONS)
                            elif engine_x + 280 <= mouse_x <= engine_x + 310:  # Next
                                engine_idx = (engine_idx + 1) % len(ENGINE_OPTIONS)
                        
                        # Player color selector (y=220) - only if not Human vs Human
                        if engine_idx != 0:  # Not Human vs Human
                            color_x, color_y = BOARD_SIZE + 20, 220
                            if color_y <= mouse_y <= color_y + 35:
                                if color_x <= mouse_x <= color_x + 30:  # Prev
                                    color_idx = (color_idx - 1) % len(COLOR_OPTIONS)
                                elif color_x + 280 <= mouse_x <= color_x + 310:  # Next
                                    color_idx = (color_idx + 1) % len(COLOR_OPTIONS)
                        
                        # Start button (y=280 or y=240 for Human vs Human)
                        start_y = 240 if engine_idx == 0 else 280
                        start_x = BOARD_SIZE + 70
                        if start_x <= mouse_x <= start_x + 200 and start_y <= mouse_y <= start_y + 50:
                            # Start the game
                            engine_name, engine = ENGINE_OPTIONS[engine_idx]
                            
                            if engine_idx == 0:  # Human vs Human
                                human_color = None
                                ai_engine = None
                            else:
                                human_color = Color.WHITE if color_idx == 0 else Color.BLACK
                                ai_engine = engine
                            
                            board = MinichessBoard(variant)
                            move_history = []
                            last_move = None
                            selected_square = None
                            legal_moves_for_selected = []
                            game_over = False
                            setup_mode = False
                            
                            # If AI plays white, it should move first
                            if ai_engine and human_color == Color.BLACK:
                                ai_thinking = True
                
                elif not game_over and not ai_thinking:
                    # Handle game clicks
                    clicked_square = screen_to_square(mouse_x, mouse_y, board, SQ_SIZE)
                    
                    if clicked_square:
                        # Check if clicking on a legal move destination
                        move_made = False
                        for move in legal_moves_for_selected:
                            if move.to_pos == clicked_square:
                                # Make the move
                                board.make_move(move)
                                move_history.append(str(move))
                                last_move = move
                                selected_square = None
                                legal_moves_for_selected = []
                                
                                # Check game over
                                if board.is_game_over():
                                    game_over = True
                                elif ai_engine:
                                    # AI's turn
                                    ai_thinking = True
                                
                                move_made = True
                                break
                        
                        if not move_made:
                            # Select a piece
                            piece = board.get_piece(clicked_square[0], clicked_square[1])
                            
                            # Check if it's player's turn
                            can_select = False
                            if ai_engine is None:
                                # Human vs Human - can always select
                                can_select = piece and piece.color == board.turn
                            elif piece and piece.color == human_color and board.turn == human_color:
                                # Playing against AI - only select if it's player's turn
                                can_select = True
                            
                            if can_select:
                                selected_square = clicked_square
                                # Get legal moves for this piece
                                all_legal_moves = board.generate_legal_moves()
                                legal_moves_for_selected = [
                                    m for m in all_legal_moves 
                                    if m.from_pos == selected_square
                                ]
                            else:
                                selected_square = None
                                legal_moves_for_selected = []
        
        # AI move logic
        if not setup_mode and not game_over and ai_thinking:
            move = ai_engine.get_move(board)
            if move:
                board.make_move(move)
                move_history.append(str(move))
                last_move = move
                
                if board.is_game_over():
                    game_over = True
            
            ai_thinking = False
        
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
            inst = font.render("Select options and press START", True, BLACK)
            screen.blit(inst, (panel_x + 20, 60))
            
            # Variant selector
            draw_selector(panel_x + 20, 100, 310, 35, VARIANT_OPTIONS, variant_idx, "Board Variant:")
            
            # Opponent engine selector
            draw_selector(panel_x + 20, 160, 310, 35, ENGINE_OPTIONS, engine_idx, "Opponent:")
            
            # Player color selector (only if not Human vs Human)
            if engine_idx != 0:
                draw_selector(panel_x + 20, 220, 310, 35, COLOR_OPTIONS, color_idx, "Play as:")
                start_y = 280
            else:
                start_y = 240
            
            # Start button
            draw_button(panel_x + 70, start_y, 200, 50, "START GAME", GREEN)
            
            # Info
            info_y = start_y + 70
            info_lines = [
                "",
                "Controls:",
                "Click to select and move",
                "R - Reset game",
                "U - Undo move",
                "Q - Quit",
            ]
            for line in info_lines:
                info_surf = font.render(line, True, BLACK)
                screen.blit(info_surf, (panel_x + 20, info_y))
                info_y += 22
        else:
            # Generate mode name for display
            if ai_engine is None:
                mode_name = "Human vs Human"
            else:
                engine_name = ENGINE_OPTIONS[engine_idx][0]
                color_name = "White" if human_color == Color.WHITE else "Black"
                mode_name = f"Human ({color_name}) vs {engine_name}"
            
            # Draw game
            draw_board(board, SQ_SIZE, selected_square, legal_moves_for_selected, last_move)
            draw_panel(board, variant, mode_name, move_history, game_over)
            
            # Draw AI thinking indicator
            if ai_thinking:
                overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 64))
                screen.blit(overlay, (0, 0))
                
                thinking_text = big_font.render("AI Thinking...", True, WHITE)
                thinking_rect = thinking_text.get_rect(center=(BOARD_SIZE//2, BOARD_SIZE//2))
                screen.blit(thinking_text, thinking_rect)
            
            # Draw game over overlay
            if game_over:
                overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                
                result = board.get_result()
                if result == "1-0":
                    result_text = "WHITE WINS!"
                elif result == "0-1":
                    result_text = "BLACK WINS!"
                else:
                    result_text = "DRAW!"
                
                game_over_text = title_font.render(result_text, True, YELLOW)
                game_over_rect = game_over_text.get_rect(center=(BOARD_SIZE//2, BOARD_SIZE//2 - 20))
                screen.blit(game_over_text, game_over_rect)
                
                reset_text = font.render("Press R to reset", True, WHITE)
                reset_rect = reset_text.get_rect(center=(BOARD_SIZE//2, BOARD_SIZE//2 + 20))
                screen.blit(reset_text, reset_rect)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
