import chess as ch
from ChessEngine import MinimaxEngine, GreedyEngine, RandomEngine
import textwrap

class Main:

    def __init__(self, board=None):
        self.board = board if board is not None else ch.Board()
        self.engine = None

    def chooseEngine(self):
        print("Choose Difficulty Level:")
        print("1 → Easy (Minimax Depth 2)")
        print("2 → Medium (Minimax Depth 3)")
        print("3 → Hard (Minimax Depth 4)")
        print("4 → Random")
        print("5 → Custom (Advanced)")

        while True:
            choice = input("Enter 1/2/3/4/5: ").strip()

            if choice == '1':
                print("Selected Easy Mode.")
                return MinimaxEngine(depth=2)
            elif choice == '2':
                print("Selected Medium Mode.")
                return MinimaxEngine(depth=3)
            elif choice == '3':
                print("Selected Hard Mode.")
                return MinimaxEngine(depth=4)
            elif choice == '4':
                print("Selected Random Mode.")
                return RandomEngine()
            elif choice == '5':
                print("Choose Engine:")
                print("1 → Minimax")
                print("2 → Greedy Material")

                while True:
                    sub_choice = input("Enter 1/2: ").strip()

                    if sub_choice == '1':
                        # ask for depth
                        while True:
                            d = input("Enter search depth for Minimax (recommended 2–4): ").strip()
                            try:
                                d = int(d)
                                if d >= 1:
                                    return MinimaxEngine(depth=d)
                                else:
                                    print("Depth must be at least 1.")
                            except:
                                print("Enter a valid integer.")

                    elif sub_choice == '2':
                        return GreedyEngine()

                    else:
                        print("Invalid choice, try again.")
            else:
                print("Invalid choice, try again.")

    def _print_legal_moves(self):
        legal = list(self.board.legal_moves)
        if not legal:
            print("No legal moves available.")
            return

        pairs = []
        for m in legal:
            try:
                san = self.board.san(m)
            except Exception:
                san = str(m)
            pairs.append(f"{san}")

        cols = 4
        lines = []
        for i in range(0, len(pairs), cols):
            lines.append("  ".join(pairs[i:i+cols]))

        print("Legal moves:")
        for ln in lines:
            print("  " + ln)

    def startGame(self):
        self.engine = self.chooseEngine()

        while True:
            side = input('Play as "b" or "w": ').strip().lower()
            if side in ('b', 'w'):
                self.player_color = ch.BLACK if side == 'b' else ch.WHITE
                break
            else:
                print("Please enter 'b' or 'w'.")

        print("Starting game. Type moves in algebraic notation (e.g. e4, Nf3, Rxh7) or UCI (e.g. g1f3).")
        print('To undo your last move type "undo". To quit type "quit".')

        print(self.board)

        try:
            while not self.board.is_game_over():
                if self.board.turn == self.player_color:

                    self._print_legal_moves()
                    user_move = input("Your move: ").strip()

                    if user_move.lower() == "quit":
                        print("Quitting.")
                        break

                    if user_move.lower() == "undo":
                        if len(self.board.move_stack) == 0:
                            print("No moves to undo.")
                        else:
                            self.board.pop()
                            print("Undid last move.")
                        print(self.board)
                        continue

                    try:
                        mv = self.board.parse_san(user_move)
                    except ValueError:
                        try:
                            mv = ch.Move.from_uci(user_move)
                            if mv not in self.board.legal_moves:
                                raise ValueError
                        except:
                            print("Invalid move. See the legal moves printed above.")
                            continue

                    self.board.push(mv)
                    print(self.board)

                else:
                    print("The engine is thinking...")
                    mv = self.engine.get_move(self.board)
                    if mv is None:
                        print("Engine has no legal moves.")
                        break

                    if mv not in self.board.legal_moves:
                        print("Engine returned illegal move; choosing fallback.")
                        mv = next(iter(self.board.legal_moves), None)
                        if mv is None:
                            break

                    self.board.push(mv)
                    print(self.board)

            else:
                print("Game over:", self.board.result())

        except (KeyboardInterrupt, EOFError):
            print("\nSession ended by user.")
        except Exception as e:
            print("Unexpected error:", e)

if __name__ == "__main__":
    game = Main()
    game.startGame()
