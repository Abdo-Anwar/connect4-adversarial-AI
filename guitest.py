import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
from connect4 import Connect4Game
import time
import threading
from tkinter import ttk


CELL_SIZE = 80
PADDING = 20
ANIMATION_DELAY = 0.02  # animation speed

class Connect4GUI:
    def __init__(self, master, minimax_depth=4):
        self.master = master
        self.master.title("Connect 4 – AI Edition")
        self.game = Connect4Game()
        self.game.set_depth(minimax_depth)
        self.ai_thinking = False

        # ------- Choose who starts -------
        self.start_var = tk.IntVar(value=2)  # default Human starts (2)
        frame = tk.Frame(master)
        frame.grid(row=0, column=0, columnspan=4, pady=10)

        self.start_frame = tk.Frame(master)
        self.start_frame.grid(row=0, column=0, columnspan=4, pady=10)
        
        
        tk.Label(self.start_frame, text="Who starts?").pack(side="left")
        tk.Radiobutton(self.start_frame, text="Human", variable=self.start_var, value=2).pack(side="left")
        tk.Radiobutton(self.start_frame, text="AI", variable=self.start_var, value=1).pack(side="left")
        tk.Button(self.start_frame, text="Start Game", command=self.start_first).pack(side="left", padx=10)

        # ------- Board setup -------
        self.width = self.game.width
        self.height = self.game.height

        canvas_width = self.width * CELL_SIZE + PADDING * 2
        canvas_height = self.height * CELL_SIZE + PADDING * 2
        self.canvas = tk.Canvas(master, width=canvas_width, height=canvas_height, bg="#003366")
        self.canvas.grid(row=1, column=0, columnspan=4)
                # Right frame for AI Tree
                
        self.tree_frame = tk.Frame(master)
        self.tree_frame.grid(row=1, column=4, padx=10, sticky="ns")

        tk.Label(self.tree_frame, text="AI Tree").pack()

        self.tree_view = ttk.Treeview(self.tree_frame)
        self.tree_view.pack(fill="both", expand=True)

        scrollbar_y = tk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree_view.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.tree_view.configure(yscrollcommand=scrollbar_y.set)

        # Buttons
        tk.Button(master, text="Minimax", command=lambda: self.set_algorithm("minimax"),
                font=("Arial", 12), width=10).grid(row=2, column=0, pady=10)
        tk.Button(master, text="Alpha-Beta", command=lambda: self.set_algorithm("alphabeta"),
                font=("Arial", 12), width=10).grid(row=2, column=1, pady=10)
        tk.Button(master, text="Expectimax", command=lambda: self.set_algorithm("expectimax"),
                font=("Arial", 12), width=10).grid(row=2, column=2, pady=10)

        self.draw_board()
        self.ai_mode = None
        self.canvas.bind("<Button-1>", self.human_move)
    def set_algorithm(self, mode):
        """Set AI algorithm without resetting the game"""
        self.ai_mode = mode
        messagebox.showinfo("Algorithm Selected", f"AI will use {mode} algorithm.")
    def start_first(self):
        
        if self.start_var.get() == 1 and self.ai_mode is None:
            messagebox.showinfo("Select Algorithm", "Please select AI algorithm first!")
            return

        # Set current player based on selection
        self.game.current_player = self.start_var.get()

        # Disable start options
        for widget in self.start_frame.winfo_children():
            widget.config(state="disabled") #ignore warning

        # Start AI turn if AI starts
        if self.game.current_player == 1:
            threading.Thread(target=self.ai_turn, daemon=True).start()
    # ---------------- BOARD DRAWING ---------------- #

   
    def draw_board(self):
        """Draw the entire board based on the current grid state"""
        self.canvas.delete("all")
        for r in range(self.height):
            for c in range(self.width):
                x1 = PADDING + c * CELL_SIZE
                y1 = PADDING + r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                self.canvas.create_oval(
                    x1 + 5, y1 + 5, x2 - 5, y2 - 5,
                    fill=self.get_color(self.game.grid[r][c]),
                    outline="#001a33",
                    width=3
                )


    def get_color(self, val):
        if val == 1:
            return "#ff0000"  # AI – Red
        elif val == 2:
            return "#ffff00"  # Human – Yellow
        else:
            return "#cccccc"  # Empty cell

    # ---------------- HUMAN MOVE ---------------- #

    def human_move(self, event):
        if self.ai_mode is None or self.game.game_over:
            return

        col = (event.x - PADDING) // CELL_SIZE
        if col < 0 or col >= self.width:
            return

        self.game.current_player = 2
        if (self.game.make_drop(col) != None):
            success = True
        else:
            success = False 

        if not success:
            messagebox.showwarning("Invalid Move", "Column is full. Choose another column.")
            print("Column full, try again!") 
            return 

       
        for row in range(self.game.height):
            if self.game.grid[row][col] == 2:
                break

        self.animate_piece(row, col, 2)
        self.after_move()


    # ---------------- ANIMATION ---------------- #

    def animate_piece(self, row, col, player):
        """Smooth falling animation to visually show a piece falling,
        but final position always matches the grid state"""
        px = PADDING + col * CELL_SIZE + CELL_SIZE // 2
        start_y = PADDING 
        target_y = PADDING + row * CELL_SIZE + CELL_SIZE // 2

        piece = self.canvas.create_oval(
            px - 30, start_y - 30, px + 30, start_y + 30,
            fill=self.get_color(player), outline="#001a33", width=3
        )

        py = start_y
        while py < target_y:
            py += 10
            if py > target_y:
                py = target_y
            self.canvas.coords(piece, px - 30, py - 30, px + 30, py + 30)
            self.canvas.update()
            time.sleep(ANIMATION_DELAY)

        
        self.draw_board()

    # ---------------- TURN HANDLING ---------------- #

    def after_move(self):
        """Check winner then let AI play"""
        winner = self.check_winner()

        if winner is not None:
            self.end_game(winner)
            return

        # AI move in separate thread to avoid freezing GUI
        threading.Thread(target=self.ai_turn, daemon=True).start()

    def ai_turn(self):
        if self.game.game_over or self.ai_thinking:
            return
        self.ai_thinking = True # prevent conccurrent threads
        col = None
        tree = None
        try:
            if self.ai_mode == "minimax":
                col, tree = self.game.ai_minimax()
            elif self.ai_mode == "alphabeta":
                col, tree = self.game.ai_alpha_beta()
            elif self.ai_mode == "expectimax":
                col, tree = self.game.ai_expectimax()
        except Exception as e:
            messagebox.showerror("Error", f"AI failed: {e}")
            self.ai_thinking = False
            return

        if col is None:
            self.ai_thinking = False
            return
        if tree:
            self.update_tree_display(tree)
        self.game.current_player = 1
        row = self.game.make_drop(col)

        self.animate_piece(row, col, 1)
       
        winner = self.check_winner()
        if winner is not None:
            self.end_game(winner)
        self.ai_thinking = False


    # ------------------ TREE VISUALIZATION ---------------- #
    def update_tree_display(self, tree):
        """Display AI tree in Treeview widget"""
        self.tree_view.delete(*self.tree_view.get_children())
        self.insert_tree_items("", tree)

    def format_tree(self, tree, indent="", last=True):
        """
        Convert nested dict tree to a string with indentation.
        """
        result = ""
        if isinstance(tree, dict):
            keys = list(tree.keys())
            for i, key in enumerate(keys):
                is_last = i == len(keys) - 1
                branch = "└─ " if is_last else "├─ "
                result += indent + branch + str(key) + "\n"
                extension = "    " if is_last else "│   "
                result += self.format_tree(tree[key], indent + extension, last=is_last)
        else:
            result += indent + f"└─ {tree}\n"
        return result
    def insert_tree_items(self, parent, tree):
        """Recursively insert items into Treeview"""
        if isinstance(tree, dict):
            for key, subtree in tree.items():
                node_text = str(key)
                if isinstance(subtree, dict) and "prob" in subtree:
                    # human node with probability
                    node_text += f" (p={subtree['prob']})"
                    child_id = self.tree_view.insert(parent, "end", text=node_text)
                    self.insert_tree_items(child_id, subtree["subtree"])
                else:
                    child_id = self.tree_view.insert(parent, "end", text=node_text)
                    self.insert_tree_items(child_id, subtree)
        else:
            self.tree_view.insert(parent, "end", text=str(tree))
    # ---------------- WIN CHECK ---------------- #

    def check_winner(self):
        if self.game.is_full():
            ai_score = self.game.calc_score(1)
            human_score = self.game.calc_score(2)
            return self.game.calc_winner(ai_score, human_score)
        return None

    def end_game(self, winner):
        self.game.game_over = True

        if winner == 1:
            messagebox.showinfo("Game Over", "AI Wins!")
        elif winner == 2:
            messagebox.showinfo("Game Over", "You Win!")
        else:
            messagebox.showinfo("Game Over", "Draw!")
        self.reset()
    # ---------------- GAME CONTROL ---------------- #

    def start_game(self, mode):
        self.ai_mode = mode
        self.reset()

    def reset(self):
        self.game.reset()
        self.draw_board()
        self.game.game_over = False


# ----------------- START APP ----------------- #

root = tk.Tk()
root.withdraw()

depth = simpledialog.askinteger(
    "Minimax Depth",
    "Enter the max depth for minimax (default=4):",
    minvalue=1, maxvalue=10
)
if depth is None:
    depth = 4

root.deiconify()

app = Connect4GUI(root, minimax_depth=depth)
root.mainloop()
