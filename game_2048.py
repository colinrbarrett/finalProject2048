import tkinter as tk
import random
import importlib
import copy

import matplotlib.pyplot as plt

class Game2048:

    def __init__(self, mode="manual", algorithm=None):
        self.size = 4
        self.board = [[0] * self.size for _ in range(self.size)]
        self.score = 0
        self.moves = ["Up", "Down", "Left", "Right"]

        ## handle ai
        self.algorithm = algorithm  # Store the chosen AI algorithm
        self.mode = mode
        
        self.spawn_tile()
        self.spawn_tile()
        self.update_board()
        
    
    def spawn_tile(self):
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4

    def update_board(self):
        return self.board, self.score
    
    
    # def handle_keypress(self, event):
    #     if self.mode == "manual":
    #         key = event.keysym
    #         if key in self.moves:
    #             old_board = [row[:] for row in self.board]
    #             self.move_board(key)
    #             if old_board != self.board:
    #                 self.spawn_tile()
    #                 self.update_board()
    #     else:
    #         return  # Ignore key presses in AI mode
        

    
    def move_board(self, direction):
        def compress(row):
            """Shift nonzero elements left."""
            new_row = [value for value in row if value != 0]
            new_row += [0] * (self.size - len(new_row))
            return new_row

        def merge(row):
            """Merge adjacent equal values."""
            for i in range(self.size - 1):
                if row[i] == row[i + 1] and row[i] != 0:
                    row[i] *= 2
                    row[i + 1] = 0
                    self.score += row[i]  # Correctly update score
            return row

        def move(row):
            """Compress, merge, then compress again."""
            return compress(merge(compress(row)))

        if direction == 'Up':
            self.board = list(map(list, zip(*self.board)))  # Transpose to treat Up as Left
            self.board = [move(row) for row in self.board]  # Move Left
            self.board = list(map(list, zip(*self.board)))  # Transpose back

        elif direction == 'Down':
            self.board = list(map(list, zip(*self.board[::-1])))  # Reverse & Transpose
            self.board = [move(row) for row in self.board]  # Move Left
            self.board = list(map(list, zip(*self.board)))[::-1]  # Transpose back & Reverse

        elif direction == 'Left':
            self.board = [move(row) for row in self.board]

        elif direction == 'Right':
            self.board = [move(row[::-1])[::-1] for row in self.board]
        
    def is_game_over(self):
        # Check for empty spaces
        for row in self.board:
            if 0 in row:
                return False
            
        # Check for adjacent tiles
        for i in range(self.size):
            for j in range(self.size):
                if i + 1 < self.size and self.board[i][j] == self.board[i + 1][j]:
                    return False  # Merge possible vertically
                if j + 1 < self.size and self.board[i][j] == self.board[i][j + 1]:
                    return False  # Merge possible horizontally

        # If no empty spaces and no valid moves, the game is over
        return True
    
    def get_valid_moves(self):
        valid_moves = []
        for move in self.moves:
            old_board = self.board  # Save the current state
            self.move_board(move)  # Try the move
            if old_board != self.board:  # If the board changed, the move is valid
                valid_moves.append(move)
            self.board = old_board  # Revert the board state

        return valid_moves
    
    def get_empty_cells(self):
        """
        Returns a list of all empty cell positions where a new tile can be placed.
        Each position is represented as a tuple (row, col).
        """
        empty_cells = [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == 0]
        return empty_cells
    
    def generate_successor(self, action):
        """
        Returns a new Game2048 instance with the board state after applying the given move.
        The original game state remains unchanged.
        """
        successor = copy.deepcopy(self)  # Create a deep copy of the current game state
        successor.move_board(action)  # Apply the move to the copied board
        

        return successor
    
    def get_max_tile(self):
        """ 
        Is going to need to be changed for efficiency
        """
        max = 0
        for i in self.board:
            for j in i:
                if j > max:
                    max = j
        return max
    


class Game2048GUI:
    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.position = []
        self.empty_space = []
        self.monotonicity = []
        self.merge_potential = []

        # Score Frame
        self.score_frame = tk.Frame(self.master)
        self.score_frame.grid(row=0, column=0, pady=10)
        self.score_label = tk.Label(self.score_frame, text=f"Score: {self.game.score}", font=('Arial', 16, 'bold'))
        self.score_label.pack()
        
        # Game Board Frame
        self.frame = tk.Frame(self.master)
        self.frame.grid(row=1, column=0)
        self.labels = [[tk.Label(self.frame, text='', width=6, height=3, font=('Arial', 24, 'bold'), relief='solid')
                        for _ in range(self.game.size)] for _ in range(self.game.size)]
        for i in range(self.game.size):
            for j in range(self.game.size):
                self.labels[i][j].grid(row=i, column=j, padx=5, pady=5)
        
        self.update_board()
        self.master.bind("<KeyPress>", self.handle_keypress)  # Bind keyboard events

    def handle_keypress(self, event):
        """Handles user input for manual play."""
        if self.game.mode == "manual":
            key = event.keysym
            if key in self.game.moves:
                old_board = [row[:] for row in self.game.board]
                self.game.move_board(key)
                if old_board != self.game.board:
                    self.game.spawn_tile()
                    self.update_board()
        else:
            return  # Ignore key presses in AI mode


    def run_ai(self):
        """Runs AI moves continuously in AI mode."""
        if not self.game.is_game_over():
            # get best move
            move, position, empty_space, monotonicity, merge = self.game.algorithm(self.game)  # AI decides move
            
            ## Store best hueristic scores
            self.position.append(position)
            self.empty_space.append(empty_space)
            self.monotonicity.append(monotonicity)
            self.merge_potential.append(merge)

            ## update board
            old_board = [row[:] for row in self.game.board]
            self.game.move_board(move)  # Apply move
            if self.game.board != old_board:
                self.game.spawn_tile()
                self.update_board()  # Update display
            self.master.after(1, self.run_ai)  # Continue AI moves
        else:
            self.plot_hueristics()


        


    def update_board(self):
        for i in range(self.game.size):
            for j in range(self.game.size):
                value = self.game.board[i][j]
                self.labels[i][j]['text'] = str(value) if value != 0 else ''
                self.labels[i][j]['bg'] = self.get_color(value)
        self.score_label.config(text=f"Score: {self.game.score}")
    
    def get_color(self, value):
        colors = {
            0: '#cdc1b4', 2: '#eee4da', 4: '#ede0c8', 8: '#f2b179', 16: '#f59563',
            32: '#f67c5f', 64: '#f65e3b', 128: '#edcf72', 256: '#edcc61',
            512: '#edc850', 1024: '#edc53f', 2048: '#edc22e'
        }
        return colors.get(value, '#3c3a32')
    
    def plot_hueristics(self):
            # Plot each list
        x = range(len(self.position))
        score = self.position + self.empty_space + self.monotonicity + self.merge_potential

        plt.plot(x, self.position, label='position')
        plt.plot(x, self.empty_space, label='empty space')
        plt.plot(x, self.monotonicity, label='mono')
        plt.plot(x, self.merge_potential, label='merge pot')
        # plt.plot(x, score, label='score')

        # Labels and legend
        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.title('Plot of 5 Lists')
        plt.legend()
        plt.grid(True)

        # Show the plot
        plt.show()

if __name__ == "__main__":

    ## find the mode we want to run in
    import argparse
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["manual", "ai"], default="manual", help="Game mode")

    # Dynamically import the selected algorithm (if AI mode is selected)
    if "ai" in parser.parse_known_args()[0].mode:
        parser.add_argument("--algorithm", choices=["Random", "Greedy", "Expectimax"], default="random", help="AI algorithm")
        args = parser.parse_args()
        ai_module = importlib.import_module(f"ai_algs.{args.algorithm}_ai")  # Import module dynamically
        ai_class = getattr(ai_module, f"{args.algorithm}Agent")  # Get the class from the module
        ai_agent = ai_class()  # Instantiate the AI agent
        ai_func = ai_agent.get_action  # Get the AI action function
    else:
        args = parser.parse_args()
        ai_func = None

    # Create the tkinter root window
    root = tk.Tk()

    # Create the Game2048 instance (game logic)
    game = Game2048(mode=args.mode, algorithm=ai_func)

    # Create the Game2048GUI instance (GUI)
    gui = Game2048GUI(root, game)  # Pass the game logic to the GUI

    # Handle the AI mode
    if args.mode == "ai":
        root.after(100, gui.run_ai)  # Start AI automatically after 100ms

    # Start the tkinter main event loop
    root.mainloop()




