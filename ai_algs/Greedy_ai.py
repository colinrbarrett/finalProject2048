import copy
import math

class GreedyAgent:
    """
    A Greedy agent for 2048 that picks the move which maximizes an immediate-state heuristic.
    Returns: (move, position_score, empty_cells, monotonicity_score, merge_potential)
    """
    def __init__(self):
        pass

    def get_action(self, game):
        best_move = None
        best_value = -math.inf
        best_features = None

        for move in game.get_valid_moves():
            # Simulate the move
            succ = copy.deepcopy(game)
            succ.move_board(move)
            # Compute features on the resulting state
            feat = self._compute_features(succ)
            # Evaluate with the same heuristic as ExpectimaxAgent
            val = self._heuristic(feat)

            if val > best_value:
                best_value = val
                best_move = move
                best_features = feat

        # Unpack features for GUI plotting
        pos = best_features['position']
        empty = best_features['empty']
        mono = best_features['monotonicity']
        merge = best_features['merge']
        return best_move, pos, empty, mono, merge

    def _compute_features(self, game):
        board = game.board
        size = game.size
        # Feature: max tile
        max_tile = game.get_max_tile()
        # Feature: empty cell count
        empties = len(game.get_empty_cells())
        # Feature: merge potential
        merge_pot = 0
        for i in range(size):
            for j in range(size):
                if j+1 < size and board[i][j] == board[i][j+1] and board[i][j] != 0:
                    merge_pot += 1
                if i+1 < size and board[i][j] == board[i+1][j] and board[i][j] != 0:
                    merge_pot += 1
        # Feature: monotonicity
        mono = 0
        # Rows
        for row in board:
            for i in range(size-1):
                if row[i] >= row[i+1]:
                    mono += (row[i] - row[i+1])
        # Columns
        for j in range(size):
            for i in range(size-1):
                if board[i][j] >= board[i+1][j]:
                    mono += (board[i][j] - board[i+1][j])
        return {
            'position': max_tile,
            'empty': empties,
            'merge': merge_pot,
            'monotonicity': mono
        }

    def _heuristic(self, features):
        # Same tuned weights used by ExpectimaxAgent
        w_pos = 1.0
        w_empty = 3.0
        w_merge = 1.2
        w_mono = 1.5
        pos_score = math.log(features['position'], 2) if features['position'] > 0 else 0
        return (
            w_pos * pos_score +
            w_empty * features['empty'] +
            w_merge * features['merge'] +
            w_mono * features['monotonicity']
        )