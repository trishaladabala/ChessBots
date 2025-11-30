# ChessBots - Minichess Game & AI Engine

A Python implementation of **Minichess** (Silverman variants) with multiple AI engines and game modes. Play against AI, watch bots battle, or play with a friend!

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-green)

## 🎮 Features

- **Multiple Board Variants**: 4x4, 4x5, 4x8, 5x5, 5x6, 6x6 Minichess boards
- **AI Engines**:
  - Random Engine
  - Greedy Engine (material-based evaluation)
  - Minimax Engine with Alpha-Beta Pruning (Depth 2-5)
- **Game Modes**:
  - Human vs Human
  - Human vs AI
  - AI vs AI (Bot Battle)
- **Interfaces**:
  - Graphical User Interface (GUI) with Pygame
  - Command Line Interface (CLI)

## 📋 Requirements

- Python 3.7+
- Pygame 2.0+ (for GUI modes)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/trishaladabala/ChessBots.git
cd ChessBots
```

2. Install dependencies:
```bash
pip install pygame
```

## 🎯 How to Play

### GUI Mode - Play Against AI

```bash
python minichess_gui.py
```

**Features:**
- Select board variant (4x4, 4x5, etc.)
- Choose opponent (Human, Random, Greedy, Minimax)
- Play as White or Black
- Click to select and move pieces
- Visual move highlighting

**Controls:**
| Key | Action |
|-----|--------|
| Click | Select/Move piece |
| R | Reset game |
| U | Undo move |
| Q | Quit |

### Bot vs Bot Mode - Watch AI Battle

```bash
python minichess_bot_vs_bot.py
```

**Features:**
- Select engines for White and Black
- Adjustable game speed
- Watch AI strategies in action

**Controls:**
| Key | Action |
|-----|--------|
| SPACE | Pause/Resume |
| R | Reset game |
| +/- | Speed up/Slow down |
| Q | Quit |

### Command Line Mode

```bash
python minichess_cli.py
```

No GUI required - runs entirely in terminal. Perfect for testing or systems without display.

## 🏁 Board Variants

| Variant | Size | Description |
|---------|------|-------------|
| 4x4 | 4×4 | Silverman 4x4 - Compact variant |
| 4x5 | 5×4 | Silverman 4x5 - Classic Minichess |
| 4x8 | 8×4 | Demi-chess - Narrow board |
| 5x5 | 5×5 | Baby Chess |
| 5x6 | 6×5 | Minit Chess |
| 6x6 | 6×6 | Los Alamos Chess (no bishops) |

## 🤖 AI Engines

### Random Engine
- Selects a random legal move
- Useful for testing and quick games

### Greedy Engine
- Evaluates immediate material gain
- Considers center control and pawn advancement
- Fast but short-sighted

### Minimax Engine
- Uses Minimax algorithm with Alpha-Beta pruning
- Configurable search depth (2-5)
- Features:
  - Material evaluation
  - Mobility bonus
  - Move ordering for better pruning
  - Checkmate detection

**Depth vs Strength:**
| Depth | Strength | Speed |
|-------|----------|-------|
| D2 | Beginner | Very Fast |
| D3 | Intermediate | Fast |
| D4 | Advanced | Moderate |
| D5 | Strong | Slower |

## 📁 Project Structure

```
ChessBots/
├── MinichessEngine.py      # Core game logic and AI engines
├── minichess_gui.py        # Play against AI (GUI)
├── minichess_bot_vs_bot.py # Watch AI vs AI battles (GUI)
├── minichess_cli.py        # Command line interface
├── pieces-basic-png/       # Chess piece images
│   ├── wp.png, bp.png      # Pawns
│   ├── wr.png, br.png      # Rooks
│   ├── wn.png, bn.png      # Knights
│   ├── wb.png, bb.png      # Bishops
│   ├── wq.png, bq.png      # Queens
│   └── wk.png, bk.png      # Kings
└── README.md
```

## 🧠 Engine Architecture

### MinichessBoard Class
- Board state representation
- Move generation (all piece types)
- Legal move filtering (check detection)
- Game state evaluation (checkmate, stalemate, draw)

### Move Generation
- Piece-specific move patterns
- Pawn: Forward moves, captures, double-move on start
- Rook: Horizontal/vertical sliding
- Bishop: Diagonal sliding
- Knight: L-shaped jumps
- Queen: Combined Rook + Bishop
- King: Single square in all directions

### Evaluation Function
```
Score = Material + Mobility + Positional Bonuses

Material Values:
- Pawn: 1.0
- Knight: 3.0
- Bishop: 3.1
- Rook: 5.0
- Queen: 9.0
```

## 🎨 Screenshots

The GUI features:
- Centered board display
- Move highlighting (last move in yellow)
- Legal move indicators (dots and rings)
- Side panel with game info and move history
- Setup screen for configuration

## 🤝 Contributing

Contributions are welcome! Ideas for improvement:
- Add more evaluation features (king safety, pawn structure)
- Implement iterative deepening
- Add transposition tables
- Create new AI algorithms (MCTS, Neural Networks)
- Add online multiplayer

## 📄 License

This project is open source and available under the MIT License.

## 👥 Authors

- [@trishaladabala](https://github.com/trishaladabala)

---

**Enjoy playing Minichess!** ♟️
