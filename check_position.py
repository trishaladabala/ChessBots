#!/usr/bin/env python3
"""Check the board position."""

import chess

# Test case 1
fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
print(f"FEN: {fen}")

try:
    board = chess.Board(fen)
    print(f"Board created successfully")
    print(board)
    print(f"\nWhite to move: {board.turn == chess.WHITE}")
    print(f"Is check: {board.is_check()}")
    print(f"Is checkmate: {board.is_checkmate()}")
    print(f"Is game over: {board.is_game_over()}")
    print(f"Number of legal moves: {len(list(board.legal_moves))}")
    
    if len(list(board.legal_moves)) > 0:
        print("\nLegal moves:")
        for move in board.legal_moves:
            print(f"  {board.san(move)}")
    else:
        print("\nNo legal moves!")
        
except Exception as e:
    print(f"Error: {e}")

# Let me create a simpler test position
print("\n" + "="*60)
print("Creating a simpler test position")
print("="*60)

# Starting position, then make some moves to create a capture opportunity
board = chess.Board()
board.push_san("e4")  # 1. e4
board.push_san("e5")  # 1... e5
board.push_san("Nf3") # 2. Nf3
board.push_san("Nc6") # 2... Nc6
board.push_san("d4")  # 3. d4
board.push_san("exd4") # 3... exd4
# Now White can recapture with the knight

print(board)
print(f"\nWhite can recapture pawn on d4")
print(f"Legal moves: {len(list(board.legal_moves))}")

from ChessEngine import GreedyEngine
engine = GreedyEngine()

print("\nMove evaluations:")
move_scores = []
for move in board.legal_moves:
    score = engine.evaluate_move_delta(board, move)
    move_scores.append((move, score))
    piece_at_to = board.piece_at(move.to_square)
    capture_info = f" (captures {piece_at_to.symbol()})" if piece_at_to else ""
    print(f"  {board.san(move):10s}: {score:+.1f}{capture_info}")

move_scores.sort(key=lambda x: x[1], reverse=True)
print(f"\nTop move: {board.san(move_scores[0][0])} with score {move_scores[0][1]:+.1f}")

best = engine.get_move(board)
print(f"Engine chose: {board.san(best)}")
