#!/usr/bin/env python3
"""
Simple command-line Minichess game
Watch two bots play without GUI (no pygame required)
"""
from MinichessEngine import (
    MinichessBoard, RandomEngine, GreedyEngine, MinimaxEngine, Color
)
import time

# Engine options
ENGINE_OPTIONS = {
    '1': ('Random', RandomEngine()),
    '2': ('Greedy', GreedyEngine()),
    '3': ('Minimax D2', MinimaxEngine(depth=2)),
    '4': ('Minimax D3', MinimaxEngine(depth=3)),
    '5': ('Minimax D4', MinimaxEngine(depth=4)),
    '6': ('Minimax D5', MinimaxEngine(depth=5)),
}

def select_engine(player):
    """Let user select an engine."""
    print(f"\nSelect engine for {player}:")
    for key, (name, _) in ENGINE_OPTIONS.items():
        print(f"  {key}. {name}")
    
    while True:
        choice = input("Enter choice (1-6): ").strip()
        if choice in ENGINE_OPTIONS:
            return ENGINE_OPTIONS[choice]
        print("Invalid choice. Try again.")

def select_variant():
    """Let user select board variant."""
    print("\nSelect board variant:")
    print("  1. 4x4 Silverman")
    print("  2. 4x5 Silverman")
    
    while True:
        choice = input("Enter choice (1-2): ").strip()
        if choice == '1':
            return '4x4'
        elif choice == '2':
            return '4x5'
        print("Invalid choice. Try again.")

def main():
    print("=" * 60)
    print("MINICHESS BOT BATTLE - COMMAND LINE")
    print("=" * 60)
    
    # Setup
    variant = select_variant()
    white_name, white_engine = select_engine("White")
    black_name, black_engine = select_engine("Black")
    
    print(f"\n{'=' * 60}")
    print(f"Variant: {variant}")
    print(f"White: {white_name}")
    print(f"Black: {black_name}")
    print(f"{'=' * 60}\n")
    
    # Create board
    board = MinichessBoard(variant)
    
    print("Initial position:")
    print(board)
    print()
    
    # Ask for speed
    while True:
        try:
            delay = float(input("Seconds between moves (0 for instant, 0.5 recommended): ").strip())
            if delay >= 0:
                break
        except ValueError:
            pass
        print("Invalid input. Enter a number >= 0")
    
    print("\nStarting game...\n")
    
    # Game loop
    move_count = 0
    start_time = time.time()
    
    while not board.is_game_over():
        # Get appropriate engine
        if board.turn == Color.WHITE:
            engine = white_engine
            engine_name = white_name
        else:
            engine = black_engine
            engine_name = black_name
        
        # Get and make move
        move = engine.get_move(board)
        
        if move is None:
            print("No legal moves available!")
            break
        
        board.make_move(move)
        move_count += 1
        
        # Display move
        turn_label = "White" if board.turn == Color.BLACK else "Black"  # Switched because turn changed
        print(f"Move {board.fullmove_number} ({turn_label} - {engine_name}): {move}")
        
        if delay > 0:
            time.sleep(delay)
            print(board)
            print()
    
    # Game over
    end_time = time.time()
    elapsed = end_time - start_time
    
    print("\n" + "=" * 60)
    print("GAME OVER")
    print("=" * 60)
    print("\nFinal position:")
    print(board)
    print()
    
    result = board.get_result()
    if result == "1-0":
        print(f"🎉 White ({white_name}) wins by checkmate!")
    elif result == "0-1":
        print(f"🎉 Black ({black_name}) wins by checkmate!")
    elif result == "1/2-1/2":
        if board.is_stalemate():
            print("Game drawn by stalemate.")
        else:
            print("Game drawn by 50-move rule.")
    
    print(f"\nTotal moves: {move_count}")
    print(f"Game duration: {elapsed:.1f} seconds")
    print(f"Moves per second: {move_count/elapsed:.2f}")
    
    # Play again?
    print("\n" + "=" * 60)
    again = input("Play another game? (y/n): ").strip().lower()
    if again == 'y':
        print("\n\n")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
    except EOFError:
        print("\n\nGame ended. Goodbye!")
