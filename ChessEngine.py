# ChessEngine.py
import chess
import random

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def material_eval(board):
    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            val = PIECE_VALUES.get(piece.piece_type, 0)
            score += val if piece.color == chess.WHITE else -val
    return score

class BaseEngine:
    def get_move(self, board):
        raise NotImplementedError

class RandomEngine(BaseEngine):
    def get_move(self, board):
        legal = list(board.legal_moves)
        if not legal:
            return None
        return random.choice(legal)

class GreedyEngine(BaseEngine):
    def evaluate_move_delta(self, board, move):
        before = material_eval(board)
        board.push(move)
        after = material_eval(board)
        board.pop()
        # We want score positive if good for side to move (before making the move)
        # When evaluating a move that's about to be played by board.turn,
        # board.turn before the push is the side making the move.
        # So simply return (after - before) as improvement for that side.
        return after - before

    def get_move(self, board):
        legal = list(board.legal_moves)
        if not legal:
            return None

        best = None
        best_score = float("-inf")

        for mv in legal:
            score = self.evaluate_move_delta(board, mv)
            # If engine is black (board.turn == False) higher 'after-before' still means good for the side to move,
            # but material_eval uses white positive / black negative. Our delta is fine as a comparator for moves by side to move.
            if score > best_score:
                best_score = score
                best = mv

        if best is None:
            return random.choice(legal)
        return best

class MinimaxEngine(BaseEngine):
    def __init__(self, depth=2):
        self.depth = depth

    def material_eval(self, board):
        return material_eval(board)

    def negamax(self, board, depth, alpha, beta, color):
        if depth == 0 or board.is_game_over():
            return color * self.material_eval(board)

        max_eval = float("-inf")
        # convert to list so push/pop won't mutate the iterator
        for mv in list(board.legal_moves):
            board.push(mv)
            val = -self.negamax(board, depth - 1, -beta, -alpha, -color)
            board.pop()

            if val > max_eval:
                max_eval = val
            if val > alpha:
                alpha = val
            if alpha >= beta:
                break

        return max_eval

    def get_move(self, board):
        legal = list(board.legal_moves)
        if not legal:
            return None

        root_color = 1 if board.turn == chess.WHITE else -1
        best = None
        best_score = float("-inf")

        for mv in legal:
            board.push(mv)
            # pass -root_color to match negamax sign convention (we already pushed mv)
            score = -self.negamax(board, self.depth - 1, float("-inf"), float("inf"), -root_color)
            board.pop()

            if score > best_score:
                best_score = score
                best = mv

        return best
