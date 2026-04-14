# Connect 4 — Adversarial AI

An interactive Connect-4 game featuring multiple adversarial AI strategies with real-time search-tree visualization.

## Features

- **Minimax** – classic exhaustive game-tree search
- **Alpha-Beta Pruning** – optimised Minimax that prunes branches that cannot influence the result
- **Expectimax** – models the opponent as a chance node (uniform random) instead of a perfect minimiser
- **Real-time tree visualisation** – after every AI move the search tree is rendered as an interactive SVG showing node types, scores, and pruned branches
- Configurable search **depth** (1–7)

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Then open <http://localhost:5000> in your browser.

## Project Structure

| File / Directory | Purpose |
|---|---|
| `game.py` | Core game logic (board, moves, win detection, heuristic evaluation) |
| `ai.py` | AI algorithms: Minimax, Alpha-Beta, Expectimax with tree recording |
| `app.py` | Flask web server exposing REST API and serving the UI |
| `templates/index.html` | Main HTML page |
| `static/css/style.css` | Styling |
| `static/js/game.js` | Front-end: board interaction and SVG tree rendering |
| `tests/` | Unit tests for game logic, AI algorithms, and Flask endpoints |

## Running Tests

```bash
python -m unittest discover -s tests -v
```

## Screenshot

![Connect 4 game board with search tree](https://github.com/user-attachments/assets/8be142fe-1801-4ecf-ba7a-679eb11043c8)