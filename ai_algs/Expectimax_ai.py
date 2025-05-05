
from game_2048 import Game2048
import numpy as np
import time
import copy

class ExpectimaxAgent:
     
    def __init__(self, depth=5):
        self.depth = depth  # Maximum depth for the expectimax tree
    
    def get_action(self, game_state: Game2048):
        """
            self.board = [[0] * self.size for _ in range(self.size)]
        """
        if game_state.score < 10000:
            self.depth = 3
        elif game_state.score > 100000:
            self.depth = 5
    


        _, move, pos, empty, mono, merge = self.max_value(game_state, 0)
        return move, pos, empty, mono, merge


    def max_value(self, game_state, current_depth):
        # make sure game is not over
        if game_state.is_game_over() or current_depth == self.depth:
            score, pos, empty, mono, merge = self.evaluation_function(game_state)
            return score, None, pos, empty, mono, merge
        
        # set up storage vars
        v = float('-10000')
        move = None
        position = 0
        empty = 0
        monotonicity = 0
        merge_pot = 0

        for action in game_state.get_valid_moves():
            successor_state = game_state.generate_successor(action)

            # find expected value of random block
            v2 , pos, emp, mono, merge= self.exp_value(successor_state, current_depth + 1)
            
            # update best move and score
            if v2 > v:
                v = v2
                move = action
                position = pos
                empty = emp
                monotonicity = mono
                merge_pot = merge

        # print(v, move,  position, empty, monotonicity, merge_pot)
        return v, move, position, empty, monotonicity, merge_pot
    
    def exp_value(self, original_game_state, current_depth):
        game_state = copy.deepcopy(original_game_state)

        # make sure game isnt over
        if game_state.is_game_over() or current_depth == self.depth:
            return self.evaluation_function(game_state)
        

        empty_cells = game_state.get_empty_cells()        

        total_score = [0, 0, 0, 0, 0]

        for cell in empty_cells:
            row, col = cell

            # Try placing a '2' (90% chance)
            game_state.board[row][col] = 2
            scores_2 = np.array(self.max_value(game_state, current_depth + 1))[[0, 2, 3, 4, 5]].astype(float)
            game_state.board[row][col] = 0

            # Try placing a '4' (10% chance)
            game_state.board[row][col] = 4
            scores_4 = np.array(self.max_value(game_state, current_depth + 1))[[0, 2, 3, 4, 5]].astype(float)
            game_state.board[row][col] = 0

            # Average weighted by spawn probability
            total_score += 0.9 * scores_2 + 0.1 * scores_4
            # print(total_score)

        return tuple(total_score)
    

    def evaluation_function(self, game_state):
        
        score = 0
        


        max_tile = game_state.get_max_tile()



        # # Empty spaces (more space = more flexibility)
        position = self.position_hueristic(game_state) * 100 // max_tile
        score += position

        # Monotonicity (reward monotonic structure)
        monotonicity_score = self.monotonicity_score(game_state) * 10
        score += monotonicity_score

        # # # Merge potential (reward adjacent pairs of the same value)
        merge_potential_score = self.merge_potential(game_state) * 5 // 1
        score += merge_potential_score

        # Empty spaces (more space = more flexibility)
        empty_space_score = self.empty_space_score(game_state) * 20
        score += empty_space_score 

        if game_state.is_game_over(): score = 0



        # High-value tile proximity (reward high-value tiles near each other)
        # high_value_tile_proximity_score = self.high_value_tile_proximity(game_state) * position // 20
        # score += high_value_tile_proximity_score


        # print(f"position {position}")
        # print(f"Empty Space Score: {empty_space_score}")
        # print(f"Monotonicity Score: {monotonicity_score}")
        # print(f"Merge Potential Score: {merge_potential_score}")
        # print(f"Total Evaluation Score: {score}\n")
        return score, position, empty_space_score,  monotonicity_score, merge_potential_score




        
    def position_hueristic(self, game_state):
        board = game_state.board
        size = len(board)

        # Weight matrix that prioritizes high values at the top-right corner
        weight_matrix = [
            [ 3,  1,  1,  3],
            [ 1,  0,  0,  1],
            [ 1,  0,  0,  1],
            [ 3,  1,  1,  3]
        ]

        weighted_score = sum(
            board[row][col] * weight_matrix[row][col]
            for row in range(size)
            for col in range(size)
        )

        return weighted_score
    
    def empty_space_score(self, game_state):
        # Encourage more empty spaces to allow better moves
        return len(game_state.get_empty_cells())
    
    def merge_potential(self, game_state):
        score = 0
        board = np.array(game_state.board)

        # Use numpy for faster pairwise comparison of adjacent tiles
        for r in range(board.shape[0]):
            for c in range(board.shape[1] - 1):  # Check horizontally
                if board[r, c] == board[r, c + 1]:
                    score += board[r, c]

        for c in range(board.shape[1]):
            for r in range(board.shape[0] - 1):  # Check vertically
                if board[r, c] == board[r + 1, c]:
                    score += board[r, c]

        return score

    def monotonicity_score(self, game_state):
        score = 0
        board = np.array(game_state.board)
        
        # Check rows and columns for monotonicity once
        for axis in [0, 1]:  # 0 = rows, 1 = columns
            for i in range(len(board)):
                line = board[i, :] if axis == 0 else board[:, i]
                score += self.is_monotonic(line)

        return score

    def is_monotonic(self, array):
        # Monotonic check for increasing or decreasing rows/columns
        increasing = np.all(array[:-1] <= array[1:]) or np.all(array[1:] == 0)
        decreasing = np.all(array[:-1] >= array[1:]) or np.all(array[1:] == 0)
        return 1 if increasing or decreasing else 0
    
    def high_value_tile_proximity(self, game_state):
        score = 0
        high_tiles = [2048, 1024, 512, 256, 128]
        for tile_value in high_tiles:
            for r in range(len(game_state.board)):
                for c in range(len(game_state.board[r])):
                    if game_state.board[r][c] == tile_value:
                        # Check proximity of high-value tiles to each other
                        for i in range(max(0, r - 1), min(len(game_state.board), r + 2)):
                            for j in range(max(0, c - 1), min(len(game_state.board[r]), c + 2)):
                                if game_state.board[i][j] == tile_value and (i != r or j != c):
                                    score += tile_value  # Reward proximity of high-value tiles
        return score

    

    
