# ChessEngine.py
import chess
import random

PIECE_VALUES = {
    chess.PAWN: 1.0,
    chess.KNIGHT: 3.2,
    chess.BISHOP: 3.33,
    chess.ROOK: 5.1,
    chess.QUEEN: 8.8,
    chess.KING: 0
}

def material_eval(board):
    """Evaluate material balance from White's perspective."""
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
        side_to_move = board.turn  # Store before pushing the move
        before = material_eval(board)
        board.push(move)
        after = material_eval(board)
        board.pop()
        
        # material_eval returns positive for White advantage, negative for Black advantage
        # delta = after - before gives us the change from White's perspective
        delta = after - before
        
        # Convert to the perspective of the side making the move:
        # - For White: positive delta = good (gaining material)
        # - For Black: negative delta = good (gaining material makes eval more negative)
        # So we flip the sign for Black to normalize: positive = good for side to move
        if side_to_move == chess.BLACK:
            delta = -delta
        
        # Add positional bonuses to avoid aimless moves
        positional_bonus = 0.0
        
        # Bonus for developing pieces (moving from starting squares)
        piece = board.piece_at(move.from_square)
        if piece:
            # Encourage knight and bishop development
            if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                # Check if moving from back rank
                from_rank = chess.square_rank(move.from_square)
                if (side_to_move == chess.WHITE and from_rank == 0) or \
                   (side_to_move == chess.BLACK and from_rank == 7):
                    positional_bonus += 0.1
            
            # Bonus for controlling center squares (e4, d4, e5, d5)
            center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
            if move.to_square in center_squares:
                positional_bonus += 0.15
            
            # Small penalty for moving to the edge (discourages Nh6, Rg8-h8 repetition)
            to_file = chess.square_file(move.to_square)
            to_rank = chess.square_rank(move.to_square)
            if to_file in [0, 7] or to_rank in [0, 7]:
                if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                    positional_bonus -= 0.05
        
        return delta + positional_bonus

    def get_move(self, board):
        legal = list(board.legal_moves)
        if not legal:
            return None

        # Collect all moves with their scores
        move_scores = []
        for mv in legal:
            score = self.evaluate_move_delta(board, mv)
            move_scores.append((mv, score))
        
        # Find the best score
        best_score = max(score for _, score in move_scores)
        
        # Collect all moves that achieve the best score
        best_moves = [mv for mv, score in move_scores if score == best_score]
        
        # Randomly choose among the best moves to add variety
        return random.choice(best_moves)

class MinimaxEngine(BaseEngine):
    """Enhanced Minimax engine with alpha-beta pruning and positional evaluation."""
    
    def __init__(self, depth=4):
        self.depth = depth
        self.nodes_searched = 0
    
    def evaluate_position(self, board):
        """
        Comprehensive position evaluation.
        Returns score from White's perspective (positive = White advantage).
        """
        # Check for game over
        if board.is_checkmate():
            # Checkmate is very bad for the side to move
            return -9999 if board.turn == chess.WHITE else 9999
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0  # Draw
        
        if board.can_claim_threefold_repetition() or board.can_claim_fifty_moves():
            return 0  # Likely draw
        
        # Material evaluation
        score = material_eval(board)
        
        # Mobility bonus (more legal moves = better, especially in opening)
        if board.fullmove_number < 10:
            mobility = len(list(board.legal_moves))
            mobility_bonus = mobility * 0.03  # Small bonus per legal move
            score += mobility_bonus if board.turn == chess.WHITE else -mobility_bonus
        
        # Add small random factor to break ties
        score += random.uniform(-0.001, 0.001)
        
        return score
    
    def order_moves(self, board, moves):
        """
        Order moves to improve alpha-beta pruning efficiency.
        Checks captures and checks first.
        """
        def move_priority(move):
            score = 0
            # Prioritize captures (especially of valuable pieces)
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                if captured_piece:
                    score += 10 + PIECE_VALUES.get(captured_piece.piece_type, 0)
            
            # Prioritize checks
            board.push(move)
            if board.is_check():
                score += 5
            board.pop()
            
            return -score  # Negative because we want higher scores first
        
        return sorted(moves, key=move_priority)
    
    def minimax(self, board, depth, alpha, beta, maximizing):
        """
        Minimax with alpha-beta pruning.
        
        Args:
            board: Current chess board
            depth: Remaining search depth
            alpha: Best score for maximizer
            beta: Best score for minimizer
            maximizing: True if maximizing player (White), False otherwise
        
        Returns:
            Best evaluation score
        """
        self.nodes_searched += 1
        
        # Base case: reached maximum depth or game over
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board)
        
        legal_moves = list(board.legal_moves)
        # Order moves for better pruning
        legal_moves = self.order_moves(board, legal_moves)
        
        if maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
            
            return min_eval
    
    def get_move(self, board):
        """Find and return the best move."""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        # Reset node counter
        self.nodes_searched = 0
        
        # Determine if we're maximizing (White) or minimizing (Black)
        maximizing = (board.turn == chess.WHITE)
        
        best_move = None
        if maximizing:
            best_score = float('-inf')
            for move in legal_moves:
                board.push(move)
                score = self.minimax(board, self.depth - 1, float('-inf'), float('inf'), False)
                board.pop()
                
                if score > best_score:
                    best_score = score
                    best_move = move
        else:
            best_score = float('inf')
            for move in legal_moves:
                board.push(move)
                score = self.minimax(board, self.depth - 1, float('-inf'), float('inf'), True)
                board.pop()
                
                if score < best_score:
                    best_score = score
                    best_move = move
        
        return best_move
