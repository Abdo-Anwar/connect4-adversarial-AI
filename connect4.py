""" 
file contetn 
class Connect4Game:
    A class to represent a Connect 4 game.
    handle the current player by 1 for AI and 2 for Human as an attribute
 methdods :
    - __init__
    - print_grid
    - is_full
    - calc_score
    - calc_heuristic
    - calc_winner
    - make_drop
    - is_valid_move

"""
import random
import time

class Connect4Game:
    def __init__(self, width=7, height=6):
        self.width = width
        self.height = height
        self.node_count = 0
        self.minimax_depth = 4  # default depth for minimax
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.current_player = random.randint(1, 2)  # 1 for AI, 2 for Human
        self.game_over = False

    def set_depth(self, depth):
        self.minimax_depth = depth

    def print_grid(self):
        for row in self.grid:
            print('|', end='')
            for cell in row:
                if cell == 0:
                    print(' ', end='|')
                elif cell == 1:
                    print('X', end='|')  # AI
                else:
                    print('O', end='|')  # Human
            print()
        
        print('-' * (self.width * 2 + 1))

        print(' ', end='')
        for i in range(self.width):
            print(f'{i}', end=' ')
        print()
    
    #  Basic LOGIC METHODS
    # --------------------------------

    def is_full(self):
        """Return True if the top row has no empty cells."""
        for col in range(self.width):
            if self.grid[0][col] == 0:
                return False
        return True

    def calc_score(self, player): 
       
        score = 0
        rows = self.height
        cols = self.width
        
        directions = [
            (0, 1),   # →
            (1, 0),   # ↓
            (1, 1),   # ↘
            (1, -1),  # ↙
        ]
        
        for r in range(rows):
            for c in range(cols):
                for dr, dc in directions: #

                    end_r = r + 3 * dr
                    end_c = c + 3 * dc

                    if 0 <= end_r < rows and 0 <= end_c < cols: # Check bounds
                        if all(self.grid[r + i*dr][c + i*dc] == player for i in range(4)): # Check 4 connect
                            score += 1
        
        return score

    def calc_heuristic(self, player):
        
        # Heuristic = score(player) - score(opponent).  tell now !
        total_heuristic = 0
        heuristic1_val = 0 # weight of consecutive 4s in any direction
        heuristic2_val = 0 # weight of pieces in strategic positions
        heuristic3_val = 0 # weight of two vertical consecutive pieces
        rows = self.height
        cols = self.width
        weight_matrix = [[1, 2, 3, 35, 3, 2, 1],
                        [2, 3, 35, 50, 35, 3, 2],
                        [2, 35, 50, 60, 50, 35, 2],
                        [2, 35, 50, 60, 50, 35, 2],
                        [2, 3, 35, 50, 35, 3, 2],
                        [1, 2, 10, 100, 10, 2, 1]]
        directions = [
            (0, 1),   # →
            (1, 0),   # ↓
            (1, 1),   # ↘
            (1, -1),  # ↙
        ]
        
        for r in range(rows):
            for c in range(cols):
                if self.grid[r][c] == player:
                    heuristic2_val += weight_matrix[r][c]
                    if r + 1 < rows and self.grid[r + 1][c] == self.grid[r][c]:
                        heuristic3_val += 10
                elif self.grid[r][c] == 3 - player:
                    heuristic2_val -= weight_matrix[r][c]
                    if r + 1 < rows and self.grid[r + 1][c] == self.grid[r][c]:
                        heuristic3_val -= 10
                for dr, dc in directions:
                    end_r = r + 3 * dr
                    end_c = c + 3 * dc

                    if 0 <= end_r < rows and 0 <= end_c < cols:
                        c_player = 0
                        c_opp = 0
                        for i in range(4):
                            if self.grid[r + i * dr][c + i * dc] == player:
                                c_player = c_player + 1
                            elif self.grid[r + i * dr][c + i * dc] == 3 - player:
                                c_opp = c_opp + 1
                        if c_player == 4 and c_opp == 0:
                            heuristic1_val += 99999
                        elif c_player == 3 and c_opp == 0:
                            heuristic1_val += 1200
                        elif c_player == 2 and c_opp == 0:
                            heuristic1_val += 67
                        elif c_player == 1 and c_opp == 0:
                            heuristic1_val += 3
                        elif c_player == 0 and c_opp == 4:
                            heuristic1_val -= 99999
                        elif c_player == 0 and c_opp == 3:
                            heuristic1_val -= 1200
                        elif c_player == 0 and c_opp == 2:
                            heuristic1_val -= 67
                        elif c_player == 0 and c_opp == 1:
                            heuristic1_val -= 3
        w1, w2, w3 = 0.9, 0.5, 0.2
        total_heuristic = (w1 * heuristic1_val) + (w2 * heuristic2_val) + (w3 * heuristic3_val)
        return total_heuristic


    def calc_winner(self, score_ai, score_human):
       
        if score_ai > score_human:
            return 1
        elif score_human > score_ai:
            return 2
        else:
            return 0

    def is_valid_move(self, col):
      
        if col < 0 or col >= self.width:
            return False
        return self.grid[0][col] == 0 

    def get_cell(self, row, col):# returns cell value
        return self.grid[row][col]

    def check_terminal_state(self):
        if self.is_full():
            ai_score = self.calc_score(1)
            human_score = self.calc_score(2)
            winner = self.calc_winner(ai_score, human_score)
            self.game_over = True
            return winner  # 1 / 2 / 0
        return None

    def reset(self):
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.current_player = random.randint(1, 2)
        self.game_over = False

    def make_drop(self, col): # returns bool
        """Used in the real game (with printing and turn switching)."""
        if self.game_over:
            print("Game is over. No more moves allowed.")
            return None

        if col < 0 or col >= self.width:
            print("Invalid column")
            return None

        for row in range(self.height - 1, -1, -1):
            if self.grid[row][col] == 0:
                self.grid[row][col] = self.current_player
                self.current_player = 3 - self.current_player
                return row

        print("Column is full. Choose another column.")
        return None
    
    def simulate_drop(self, col, player): # returns row played in
        """used by AI simulation only (no prints, no switching)."""
        if self.game_over: # keep it here for now may be later we will remove it or add actioin for it 
            return None

        if col < 0 or col >= self.width: # may be we will remove it later and add checks in the main method
            return None
       
        for row in range(self.height - 1, -1, -1):
            if self.grid[row][col] == 0:    # Find lowest empty row
                self.grid[row][col] = player
                return row
            
        return None

    def undo_drop(self, col, row):
        """undo a simulated drop"""        
        self.grid[row][col] = 0
            

#  Algorithmes  METHODS
# --------------------------------
    def minimax(self, depth, maximizing_player): # maximizing_player = True for AI 
        """
        Returns: (value, tree)
        tree: dict {col: subtree_value} for children
        """
        self.node_count += 1

        if depth == 0 or self.is_full():
            val = self.calc_heuristic(1)
            return val, val
        tree = {}
        
        if maximizing_player:
            max_eval = float('-inf')
            for col in range(self.width):  
                row = self.simulate_drop(col, 1)
                if row is None: # dont calculate for invalid moves in the SIMULATION
                    continue
                eval , subtree = self.minimax(depth-1, False)
                tree[col] = subtree
                max_eval = max(max_eval, eval)
                self.undo_drop(col, row)
            return max_eval, tree
        
        else:
            min_eval = float('inf')
            for col in range(self.width):
                row = self.simulate_drop(col, 2)
                if row is None: # dont calculate for invalid moves
                    continue
                eval , subtree = self.minimax(depth-1, True)
                tree[col] = subtree
                min_eval = min(min_eval, eval)
                self.undo_drop(col, row)
            return min_eval, tree
        
    def alpha_beta(self, depth, alpha, beta, maximizing_player): # maximizing_player = True for AI 
        self.node_count += 1
        if depth == 0 or self.is_full():
            val = self.calc_heuristic(2)
            return val, val
        bst_eval = float('-inf') if maximizing_player else float('inf')
        best_tree = {}
        
        for col in range(self.width):  
                # "!!!!!!!!!
                row = self.simulate_drop(col, 1)
                if row is None: # dont calculate for invalid moves in the SIMULATION
                    continue
                eval_val , subtree = self.alpha_beta(depth - 1, alpha, beta, 1 ^ maximizing_player)
                # bst_eval = max(bst_eval, eval) if maximizing_player else min(bst_eval, eval)
                best_tree[col] = subtree
                self.undo_drop(col, row)
                if maximizing_player:
                    bst_eval = max(bst_eval, eval_val)
                    
                    alpha = max(alpha, eval_val)
                else:
                    
                    bst_eval = min(bst_eval, eval_val)
                    beta = min(beta, eval_val)
                if alpha >= beta:
                    break
        return bst_eval, best_tree

    def exex_minimax(self, depth, maximizing_player):
        self.node_count += 1
        if depth == 0 or self.is_full():
            val = self.calc_heuristic(1)  # always for ai
            return val, val
        
        tree = {}
        if maximizing_player:
            max_eval = float('-inf')
            for col in range(self.width):
                row = self.simulate_drop(col, 1)
                if row is None:
                    continue
                eval_val, subtree = self.exex_minimax(depth - 1, False)
                tree[col] = subtree
                max_eval = max(max_eval, eval_val)
                self.undo_drop(col, row)
            return max_eval, tree
        
        else:  # human
            total = 0
            count = 0
            
            for col in range(self.width):
                if not self.is_valid_move(col):
                    continue
                
                cols = [col]
                if col - 1 >= 0 and self.is_valid_move(col-1):
                    cols.append(col-1)
                if col + 1 < self.width and self.is_valid_move(col+1):
                    cols.append(col+1)
                
                probs = [0.6, 0.2, 0.2][:len(cols)]
                expectation = 0
                
                for p, c in zip(probs, cols):
                    row = self.simulate_drop(c, 2)
                    if row is None:
                        continue
                    eval_val, _ = self.exex_minimax(depth - 1, True)  # ignore subtree for human
                    expectation += p * eval_val
                    self.undo_drop(c, row)

                total += expectation
                count += 1

            if count == 0:
                val = self.calc_heuristic(1)
                return val, {}
            
            return total / count, {}

    def ai_minimax(self): 
        """let ai pick best column based on minimax"""
        best_val  = float('-inf')
        best_col = None
        full_tree = {}

        for col in range(self.width): # evaluate minimax after every move
            row = self.simulate_drop(col, 1) # test
            if row is None: # dont calculate for invalid moves in the REAL BOARD
                continue
            
            val, tree = self.minimax(self.minimax_depth-1, False) # opponent
            full_tree[col] = tree
            self.undo_drop(col, row)
            
            if val > best_val:
                best_val = val
                best_col = col

        return best_col , full_tree
    
    def ai_alpha_beta(self):
        """let ai pick best column based on alpha-beta pruning"""
        best_val  = float('-inf')
        best_col = None
        full_tree = {}

        for col in range(self.width): # evaluate minimax after every move
            row = self.simulate_drop(col, 1) # test
            if row is None: # dont calculate for invalid moves in the REAL BOARD
                continue
            
            val, tree = self.alpha_beta(self.minimax_depth-1, float('-inf'), float('inf'), False) # opponent
            full_tree[col] = tree
            self.undo_drop(col, row)
            
            if val > best_val:
                best_val = val
                best_col = col

        return best_col , full_tree

    def ai_expectimax(self):
        """let ai pick best column based on expectimax"""
        best_val = float('-inf')
        best_col = None
        full_tree = {}

        for col in range(self.width): # evaluate minimax after every move
            row = self.simulate_drop(col, 1) # test
            if row is None: # dont calculate for invalid moves in the REAL BOARD
                continue
            
            val, tree = self.exex_minimax(self.minimax_depth - 1, False) # opponent
            full_tree[col] = tree
            self.undo_drop(col, row)

            if val > best_val:
                best_val = val
                best_col = col

        return best_col, full_tree
# test 
if __name__ == "__main__": 
    game = Connect4Game()
    # depth = int(input("Enter the max depth for minimax (default=4): ") or 4)
    # game.set_depth(depth)
    game.print_grid()

    # try several depths K values
    for depth in [2, 3, 4, 5]:
        game.set_depth(depth)
        print(f"\n=== Depth K = {depth} ===")

        # --- Minimax ---
        game.reset()
        game.node_count = 0
        start = time.time()
        best_col, _ = game.ai_minimax()
        t1 = time.time() - start
        nodes1 = game.node_count
        print(f"Minimax:     best_col={best_col},  time={t1:.3f}s,  nodes={nodes1}")

        # --- Alpha‑Beta ---
        game.reset()
        game.node_count = 0
        start = time.time()
        best_col, _ = game.ai_alpha_beta()
        t2 = time.time() - start
        nodes2 = game.node_count 
        print(f"Alpha‑Beta:  best_col={best_col},  time={t2:.3f}s,  nodes={nodes2}")

        # --- Expectimax ---
        game.reset()
        game.node_count = 0
        start = time.time()
        best_col, _ = game.ai_expectimax()
        t3 = time.time() - start
        nodes3 = game.node_count 
        print(f"Expectimax:  best_col={best_col},  time={t3:.3f}s,  nodes={nodes3}")
