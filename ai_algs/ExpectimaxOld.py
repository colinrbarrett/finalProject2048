
from game_2048 import Game2048

class ExpectimaxAgent:
     
    def __init__(self, depth=5):
        self.depth = depth  # Maximum depth for the expectimax tree
    
    def get_action(self, game_state: Game2048):
        """
            self.board = [[0] * self.size for _ in range(self.size)]
        """
        _, move = self.max_value(game_state, 0)
        return move


        

    def max_value(self, game_state, current_depth):
        # make sure game is not over
        if game_state.is_game_over() or current_depth == self.depth:
            return self.evaluation_function(game_state), None
        

        # set up storage vars
        v = float('-10000')
        move = None

        for action in game_state.get_valid_moves():
            successor_state = game_state.generate_successor(action)

            # find expected value of random block
            v2 = self.exp_value(successor_state, current_depth + 1)
            
            # update best move and score
            if v2 > v:
                v = v2
                move = action
        return v, move
    
    def exp_value(self, game_state, current_depth):

        # make sure game isnt over
        if game_state.is_game_over() or current_depth == self.depth:
            return self.evaluation_function(game_state)
        

        empty_cells = game_state.get_empty_cells()

        # when would this matter?
        if not empty_cells:
            return self.evaluation_function(game_state)
        

        total_score = 0

        for cell in empty_cells:
            row, col = cell

            # Try placing a '2' (90% chance)
            game_state.board[row][col] = 2
            score_2 = self.max_value(game_state, current_depth + 1)[0]
            game_state.board[row][col] = 0  # Undo move

            # Try placing a '4' (10% chance)
            game_state.board[row][col] = 4
            score_4 = self.max_value(game_state, current_depth + 1)[0]
            game_state.board[row][col] = 0  # Undo move

            # Average weighted by spawn probability
            total_score += 0.9 * score_2 + 0.1 * score_4

        return total_score / len(empty_cells)
    


    def evaluation_function(self, game_state):
            # Basic heuristic: sum of all tiles
            return sum(sum(row) for row in game_state.board)




        

    

    
