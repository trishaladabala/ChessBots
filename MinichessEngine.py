# MinichessEngine.py
"""
Minichess game logic and AI engines for 4x4 and 4x5 variants.
Based on Silverman's Minichess variants.
"""
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple

class PieceType(Enum):
    PAWN = 'P'
    ROOK = 'R'
    BISHOP = 'B'
    KNIGHT = 'N'
    QUEEN = 'Q'
    KING = 'K'

class Color(Enum):
    WHITE = 'white'
    BLACK = 'black'

@dataclass
class Piece:
    type: PieceType
    color: Color
    
    def __str__(self):
        symbol = self.type.value
        return symbol if self.color == Color.WHITE else symbol.lower()

@dataclass
class Move:
    from_pos: Tuple[int, int]  # (row, col)
    to_pos: Tuple[int, int]
    piece: Piece
    captured: Optional[Piece] = None
    
    def __str__(self, cols='abcdef'):
        from_str = f"{cols[self.from_pos[1]]}{self.from_pos[0] + 1}"
        to_str = f"{cols[self.to_pos[1]]}{self.to_pos[0] + 1}"
        if self.captured:
            return f"{from_str}x{to_str}"
        return f"{from_str}-{to_str}"

class MinichessBoard:
    """Represents a Minichess board (supports multiple variants)."""
    
    def __init__(self, variant='4x5'):
        """
        Initialize board.
        Supported variants: '4x4', '4x5', '4x8', '5x5', '5x6', '6x6'
        """
        self.variant = variant
        self.pawn_double_move = False  # Will be set per variant
        
        # Set board dimensions
        if variant in ['4x4', '4x5']:
            self.rows, self.cols = (4, 4) if variant == '4x4' else (5, 4)
        elif variant == '4x8':
            self.rows, self.cols = 8, 4
        elif variant == '5x5':
            self.rows, self.cols = 5, 5
        elif variant == '5x6':
            self.rows, self.cols = 6, 5
        elif variant == '6x6':
            self.rows, self.cols = 6, 6
        else:
            raise ValueError(f"Unknown variant: {variant}")
        
        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.turn = Color.WHITE
        self.move_history = []
        self.fullmove_number = 1
        self.halfmove_clock = 0
        self._setup_board()
    
    def _setup_board(self):
        """Setup initial position based on variant."""
        if self.variant == '4x4':
            # 4x4 Silverman: R Q K R / P P P P / p p p p / r q k r
            white_pieces = [PieceType.ROOK, PieceType.QUEEN, PieceType.KING, PieceType.ROOK]
            black_pieces = [PieceType.ROOK, PieceType.QUEEN, PieceType.KING, PieceType.ROOK]
            for col, ptype in enumerate(white_pieces):
                self.board[0][col] = Piece(ptype, Color.WHITE)
            for col in range(4):
                self.board[1][col] = Piece(PieceType.PAWN, Color.WHITE)
                self.board[2][col] = Piece(PieceType.PAWN, Color.BLACK)
            for col, ptype in enumerate(black_pieces):
                self.board[3][col] = Piece(ptype, Color.BLACK)
        
        elif self.variant == '4x5':
            # 4x5 Silverman: R Q K R / P P P P / empty / p p p p / r q k r
            self.pawn_double_move = True
            white_pieces = [PieceType.ROOK, PieceType.QUEEN, PieceType.KING, PieceType.ROOK]
            black_pieces = [PieceType.ROOK, PieceType.QUEEN, PieceType.KING, PieceType.ROOK]
            for col, ptype in enumerate(white_pieces):
                self.board[0][col] = Piece(ptype, Color.WHITE)
            for col in range(4):
                self.board[1][col] = Piece(PieceType.PAWN, Color.WHITE)
                self.board[3][col] = Piece(PieceType.PAWN, Color.BLACK)
            for col, ptype in enumerate(black_pieces):
                self.board[4][col] = Piece(ptype, Color.BLACK)
        
        elif self.variant == '4x8':
            # 4x8 Demi-chess: K B N R / P P P P / ... / p p p p / k b n r
            white_pieces = [PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
            black_pieces = [PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
            for col, ptype in enumerate(white_pieces):
                self.board[0][col] = Piece(ptype, Color.WHITE)
            for col in range(4):
                self.board[1][col] = Piece(PieceType.PAWN, Color.WHITE)
                self.board[6][col] = Piece(PieceType.PAWN, Color.BLACK)
            for col, ptype in enumerate(black_pieces):
                self.board[7][col] = Piece(ptype, Color.BLACK)
        
        elif self.variant == '5x5':
            # Baby Chess: K Q B N R / P P P P P / empty / p p p p p / k q b n r
            self.pawn_double_move = True
            white_pieces = [PieceType.KING, PieceType.QUEEN, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
            black_pieces = [PieceType.KING, PieceType.QUEEN, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
            for col, ptype in enumerate(white_pieces):
                self.board[0][col] = Piece(ptype, Color.WHITE)
            for col in range(5):
                self.board[1][col] = Piece(PieceType.PAWN, Color.WHITE)
                self.board[3][col] = Piece(PieceType.PAWN, Color.BLACK)
            for col, ptype in enumerate(black_pieces):
                self.board[4][col] = Piece(ptype, Color.BLACK)
        
        elif self.variant == '5x6':
            # Minit Chess: K Q B N R / P P P P P / ... / p p p p p / k q b n r
            self.pawn_double_move = True
            white_pieces = [PieceType.KING, PieceType.QUEEN, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
            black_pieces = [PieceType.KING, PieceType.QUEEN, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
            for col, ptype in enumerate(white_pieces):
                self.board[0][col] = Piece(ptype, Color.WHITE)
            for col in range(5):
                self.board[1][col] = Piece(PieceType.PAWN, Color.WHITE)
                self.board[4][col] = Piece(PieceType.PAWN, Color.BLACK)
            for col, ptype in enumerate(black_pieces):
                self.board[5][col] = Piece(ptype, Color.BLACK)
        
        elif self.variant == '6x6':
            # Los Alamos Chess: R N Q K N R / P P P P P P / ... / p p p p p p / r n q k n r
            white_pieces = [PieceType.ROOK, PieceType.KNIGHT, PieceType.QUEEN, PieceType.KING, PieceType.KNIGHT, PieceType.ROOK]
            black_pieces = [PieceType.ROOK, PieceType.KNIGHT, PieceType.QUEEN, PieceType.KING, PieceType.KNIGHT, PieceType.ROOK]
            for col, ptype in enumerate(white_pieces):
                self.board[0][col] = Piece(ptype, Color.WHITE)
            for col in range(6):
                self.board[1][col] = Piece(PieceType.PAWN, Color.WHITE)
                self.board[4][col] = Piece(PieceType.PAWN, Color.BLACK)
            for col, ptype in enumerate(black_pieces):
                self.board[5][col] = Piece(ptype, Color.BLACK)
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get piece at position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.board[row][col]
        return None
    
    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        """Set piece at position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.board[row][col] = piece
    
    def is_valid_pos(self, row: int, col: int) -> bool:
        """Check if position is on board."""
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def generate_legal_moves(self) -> List[Move]:
        """Generate all legal moves for current player."""
        moves = []
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board[row][col]
                if piece and piece.color == self.turn:
                    moves.extend(self._generate_piece_moves(row, col, piece))
        
        # Filter out moves that leave king in check
        legal_moves = []
        for move in moves:
            if not self._move_leaves_king_in_check(move):
                legal_moves.append(move)
        
        return legal_moves
    
    def _generate_piece_moves(self, row: int, col: int, piece: Piece) -> List[Move]:
        """Generate pseudo-legal moves for a piece."""
        moves = []
        
        if piece.type == PieceType.PAWN:
            moves.extend(self._generate_pawn_moves(row, col, piece))
        elif piece.type == PieceType.ROOK:
            moves.extend(self._generate_rook_moves(row, col, piece))
        elif piece.type == PieceType.BISHOP:
            moves.extend(self._generate_bishop_moves(row, col, piece))
        elif piece.type == PieceType.KNIGHT:
            moves.extend(self._generate_knight_moves(row, col, piece))
        elif piece.type == PieceType.QUEEN:
            moves.extend(self._generate_queen_moves(row, col, piece))
        elif piece.type == PieceType.KING:
            moves.extend(self._generate_king_moves(row, col, piece))
        
        return moves
    
    def _generate_pawn_moves(self, row: int, col: int, piece: Piece) -> List[Move]:
        """Generate pawn moves."""
        moves = []
        direction = 1 if piece.color == Color.WHITE else -1
        
        # Forward move
        new_row = row + direction
        if self.is_valid_pos(new_row, col) and self.board[new_row][col] is None:
            moves.append(Move((row, col), (new_row, col), piece))
            
            # Double move on first move (for variants that allow it)
            if self.pawn_double_move:
                # Determine starting row based on variant
                if self.variant in ['4x5', '5x6']:
                    start_row = 1 if piece.color == Color.WHITE else (self.rows - 2)
                elif self.variant == '5x5':
                    start_row = 1 if piece.color == Color.WHITE else 3
                else:
                    start_row = -1  # No double move
                
                if row == start_row:
                    new_row2 = row + 2 * direction
                    if self.is_valid_pos(new_row2, col) and self.board[new_row2][col] is None:
                        moves.append(Move((row, col), (new_row2, col), piece))
        
        # Captures
        for dc in [-1, 1]:
            new_row = row + direction
            new_col = col + dc
            if self.is_valid_pos(new_row, new_col):
                target = self.board[new_row][new_col]
                if target and target.color != piece.color:
                    moves.append(Move((row, col), (new_row, new_col), piece, target))
        
        return moves
    
    def _generate_rook_moves(self, row: int, col: int, piece: Piece) -> List[Move]:
        """Generate rook moves."""
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, max(self.rows, self.cols)):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.is_valid_pos(new_row, new_col):
                    break
                
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append(Move((row, col), (new_row, new_col), piece))
                else:
                    if target.color != piece.color:
                        moves.append(Move((row, col), (new_row, new_col), piece, target))
                    break
        
        return moves
    
    def _generate_queen_moves(self, row: int, col: int, piece: Piece) -> List[Move]:
        """Generate queen moves (rook + bishop)."""
        moves = []
        # Straight lines (like rook)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, max(self.rows, self.cols)):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.is_valid_pos(new_row, new_col):
                    break
                
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append(Move((row, col), (new_row, new_col), piece))
                else:
                    if target.color != piece.color:
                        moves.append(Move((row, col), (new_row, new_col), piece, target))
                    break
        
        return moves
    
    def _generate_bishop_moves(self, row: int, col: int, piece: Piece) -> List[Move]:
        """Generate bishop moves."""
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, max(self.rows, self.cols)):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.is_valid_pos(new_row, new_col):
                    break
                
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append(Move((row, col), (new_row, new_col), piece))
                else:
                    if target.color != piece.color:
                        moves.append(Move((row, col), (new_row, new_col), piece, target))
                    break
        
        return moves
    
    def _generate_knight_moves(self, row: int, col: int, piece: Piece) -> List[Move]:
        """Generate knight moves."""
        moves = []
        knight_offsets = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        
        for dr, dc in knight_offsets:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_pos(new_row, new_col):
                target = self.board[new_row][new_col]
                if target is None or target.color != piece.color:
                    moves.append(Move((row, col), (new_row, new_col), piece, target))
        
        return moves
    
    def _generate_king_moves(self, row: int, col: int, piece: Piece) -> List[Move]:
        """Generate king moves."""
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_pos(new_row, new_col):
                target = self.board[new_row][new_col]
                if target is None or target.color != piece.color:
                    moves.append(Move((row, col), (new_row, new_col), piece, target))
        
        return moves
    
    def _find_king(self, color: Color) -> Optional[Tuple[int, int]]:
        """Find king position for given color."""
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board[row][col]
                if piece and piece.type == PieceType.KING and piece.color == color:
                    return (row, col)
        return None
    
    def _is_square_attacked(self, row: int, col: int, by_color: Color) -> bool:
        """Check if a square is attacked by given color."""
        # Check all opponent pieces
        for r in range(self.rows):
            for c in range(self.cols):
                piece = self.board[r][c]
                if piece and piece.color == by_color:
                    # Generate moves for this piece (without check filtering)
                    attacks = self._generate_piece_moves(r, c, piece)
                    for move in attacks:
                        if move.to_pos == (row, col):
                            return True
        return False
    
    def is_in_check(self, color: Color) -> bool:
        """Check if given color's king is in check."""
        king_pos = self._find_king(color)
        if not king_pos:
            return False
        
        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self._is_square_attacked(king_pos[0], king_pos[1], opponent_color)
    
    def _move_leaves_king_in_check(self, move: Move) -> bool:
        """Check if a move would leave own king in check."""
        # Make move temporarily
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        
        saved_piece = self.board[to_row][to_col]
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        
        in_check = self.is_in_check(move.piece.color)
        
        # Undo move
        self.board[from_row][from_col] = self.board[to_row][to_col]
        self.board[to_row][to_col] = saved_piece
        
        return in_check
    
    def make_move(self, move: Move) -> bool:
        """Make a move on the board."""
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        
        # Update board
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        
        # Update counters
        if move.captured or move.piece.type == PieceType.PAWN:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        if self.turn == Color.BLACK:
            self.fullmove_number += 1
        
        # Switch turn
        self.turn = Color.BLACK if self.turn == Color.WHITE else Color.WHITE
        
        # Add to history
        self.move_history.append(move)
        
        return True
    
    def is_checkmate(self) -> bool:
        """Check if current player is checkmated."""
        if not self.is_in_check(self.turn):
            return False
        return len(self.generate_legal_moves()) == 0
    
    def is_stalemate(self) -> bool:
        """Check if current player is stalemated."""
        if self.is_in_check(self.turn):
            return False
        return len(self.generate_legal_moves()) == 0
    
    def is_game_over(self) -> bool:
        """Check if game is over."""
        if self.is_checkmate() or self.is_stalemate():
            return True
        # Draw by 50 move rule
        if self.halfmove_clock >= 50:
            return True
        return False
    
    def get_result(self) -> str:
        """Get game result."""
        if self.is_checkmate():
            return "0-1" if self.turn == Color.WHITE else "1-0"
        elif self.is_stalemate():
            return "1/2-1/2"
        elif self.halfmove_clock >= 50:
            return "1/2-1/2"
        return "*"
    
    def copy(self):
        """Create a deep copy of the board."""
        new_board = MinichessBoard(self.variant)
        new_board.board = [[self.board[r][c] for c in range(self.cols)] for r in range(self.rows)]
        new_board.turn = self.turn
        new_board.move_history = self.move_history.copy()
        new_board.fullmove_number = self.fullmove_number
        new_board.halfmove_clock = self.halfmove_clock
        return new_board
    
    def __str__(self):
        """String representation of board."""
        lines = []
        for row in range(self.rows - 1, -1, -1):
            line = f"{row + 1} "
            for col in range(self.cols):
                piece = self.board[row][col]
                line += str(piece) if piece else "."
                line += " "
            lines.append(line)
        col_labels = " " + " ".join("abcdef"[:self.cols])
        lines.append(col_labels)
        return "\n".join(lines)


# ============= AI ENGINES =============

PIECE_VALUES = {
    PieceType.PAWN: 1.0,
    PieceType.KNIGHT: 3.0,
    PieceType.BISHOP: 3.1,
    PieceType.ROOK: 5.0,
    PieceType.QUEEN: 9.0,
    PieceType.KING: 0
}

def material_eval(board: MinichessBoard) -> float:
    """Evaluate material balance from White's perspective."""
    score = 0.0
    for row in range(board.rows):
        for col in range(board.cols):
            piece = board.board[row][col]
            if piece:
                val = PIECE_VALUES.get(piece.type, 0)
                score += val if piece.color == Color.WHITE else -val
    return score

class MinichessEngine:
    """Base class for Minichess engines."""
    def get_move(self, board: MinichessBoard) -> Optional[Move]:
        raise NotImplementedError

class RandomEngine(MinichessEngine):
    """Random move engine."""
    def get_move(self, board: MinichessBoard) -> Optional[Move]:
        legal_moves = board.generate_legal_moves()
        if not legal_moves:
            return None
        return random.choice(legal_moves)

class GreedyEngine(MinichessEngine):
    """Greedy engine that picks moves based on immediate material gain."""
    
    def evaluate_move_delta(self, board: MinichessBoard, move: Move) -> float:
        """Evaluate a move's value."""
        side_to_move = board.turn
        before = material_eval(board)
        
        # Temporarily make move
        board_copy = board.copy()
        board_copy.make_move(move)
        after = material_eval(board_copy)
        
        delta = after - before
        if side_to_move == Color.BLACK:
            delta = -delta
        
        # Positional bonuses
        positional_bonus = 0.0
        
        # Bonus for center control
        center_squares = [(1, 1), (1, 2), (2, 1), (2, 2)] if board.variant == '4x4' else [(2, 1), (2, 2)]
        if move.to_pos in center_squares:
            positional_bonus += 0.15
        
        # Bonus for pawn advancement
        if move.piece.type == PieceType.PAWN:
            to_row = move.to_pos[0]
            if side_to_move == Color.WHITE:
                positional_bonus += to_row * 0.1
            else:
                positional_bonus += (board.rows - 1 - to_row) * 0.1
        
        return delta + positional_bonus
    
    def get_move(self, board: MinichessBoard) -> Optional[Move]:
        legal_moves = board.generate_legal_moves()
        if not legal_moves:
            return None
        
        move_scores = [(move, self.evaluate_move_delta(board, move)) for move in legal_moves]
        best_score = max(score for _, score in move_scores)
        best_moves = [move for move, score in move_scores if score == best_score]
        
        return random.choice(best_moves)

class MinimaxEngine(MinichessEngine):
    """Minimax engine with alpha-beta pruning."""
    
    def __init__(self, depth=4):
        self.depth = depth
        self.nodes_searched = 0
    
    def evaluate_position(self, board: MinichessBoard) -> float:
        """Evaluate position from White's perspective."""
        # Check for game over
        if board.is_checkmate():
            return -9999 if board.turn == Color.WHITE else 9999
        
        if board.is_stalemate() or board.halfmove_clock >= 50:
            return 0
        
        score = material_eval(board)
        
        # Mobility bonus
        if board.fullmove_number < 5:
            mobility = len(board.generate_legal_moves())
            mobility_bonus = mobility * 0.05
            score += mobility_bonus if board.turn == Color.WHITE else -mobility_bonus
        
        # Small random factor
        score += random.uniform(-0.001, 0.001)
        
        return score
    
    def order_moves(self, board: MinichessBoard, moves: List[Move]) -> List[Move]:
        """Order moves for better pruning."""
        def move_priority(move):
            score = 0
            if move.captured:
                score += 10 + PIECE_VALUES.get(move.captured.type, 0)
            
            # Check if move gives check
            board_copy = board.copy()
            board_copy.make_move(move)
            opponent = Color.BLACK if board.turn == Color.WHITE else Color.WHITE
            if board_copy.is_in_check(opponent):
                score += 5
            
            return -score
        
        return sorted(moves, key=move_priority)
    
    def minimax(self, board: MinichessBoard, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Minimax with alpha-beta pruning."""
        self.nodes_searched += 1
        
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board)
        
        legal_moves = board.generate_legal_moves()
        legal_moves = self.order_moves(board, legal_moves)
        
        if maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                board_copy = board.copy()
                board_copy.make_move(move)
                eval_score = self.minimax(board_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board_copy = board.copy()
                board_copy.make_move(move)
                eval_score = self.minimax(board_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def get_move(self, board: MinichessBoard) -> Optional[Move]:
        """Find best move."""
        legal_moves = board.generate_legal_moves()
        if not legal_moves:
            return None
        
        self.nodes_searched = 0
        maximizing = (board.turn == Color.WHITE)
        
        best_move = None
        if maximizing:
            best_score = float('-inf')
            for move in legal_moves:
                board_copy = board.copy()
                board_copy.make_move(move)
                score = self.minimax(board_copy, self.depth - 1, float('-inf'), float('inf'), False)
                if score > best_score:
                    best_score = score
                    best_move = move
        else:
            best_score = float('inf')
            for move in legal_moves:
                board_copy = board.copy()
                board_copy.make_move(move)
                score = self.minimax(board_copy, self.depth - 1, float('-inf'), float('inf'), True)
                if score < best_score:
                    best_score = score
                    best_move = move
        
        return best_move
