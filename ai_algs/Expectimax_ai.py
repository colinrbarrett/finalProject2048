import copy
import math

class ExpectimaxAgent:
    """
    An Expectimax agent for 2048 that performs depth-limited expectimax search.
    Returns: (move, position_score, empty_cells, monotonicity_score, merge_potential)
    """
    def __init__(self, depth=3):  # increased default depth for better foresight
        self.depth = depth

    def get_action(self, game):
        # Maximize over valid moves
        best_move = None
        best_value = -math.inf
        best_features = None
        for move in game.get_valid_moves():
            succ = copy.deepcopy(game)
            succ.move_board(move)
            value, features = self._expectimax(succ, self.depth - 1, True)
            if value > best_value:
                best_value = value
                best_move = move
                best_features = features

        # Unpack features for GUI plotting
        pos = best_features['position']
        empty = best_features['empty']
        mono = best_features['monotonicity']
        merge = best_features['merge']
        return best_move, pos, empty, mono, merge

    def _expectimax(self, game, depth, chance):
        # Terminal check
        if depth == 0 or game.is_game_over():
            feat = self._compute_features(game)
            return self._heuristic(feat), feat

        if chance:
            # Chance node: average over all tile spawns
            empties = game.get_empty_cells()
            if not empties:
                feat = self._compute_features(game)
                return self._heuristic(feat), feat
            total = 0.0
            for r, c in empties:
                for tile, prob in [(2, 0.9), (4, 0.1)]:
                    succ = copy.deepcopy(game)
                    succ.board[r][c] = tile
                    val, _ = self._expectimax(succ, depth - 1, False)
                    total += (prob * val) / len(empties)
            feat = self._compute_features(game)
            return total, feat
        else:
            # Max node: pick best move
            best = -math.inf
            best_feat = None
            for move in game.get_valid_moves():
                succ = copy.deepcopy(game)
                succ.move_board(move)
                val, feat = self._expectimax(succ, depth - 1, True)
                if val > best:
                    best = val
                    best_feat = feat
            return best, best_feat

    def _compute_features(self, game):
        board = game.board
        size = game.size
        # Feature 1: Max tile
        max_tile = game.get_max_tile()
        # Feature 2: Empty cells
        empties = len(game.get_empty_cells())
        # Feature 3: Merge potential
        merge_pot = 0
        for i in range(size):
            for j in range(size):
                if j+1 < size and board[i][j] == board[i][j+1] and board[i][j] != 0:
                    merge_pot += 1
                if i+1 < size and board[i][j] == board[i+1][j] and board[i][j] != 0:
                    merge_pot += 1
        # Feature 4: Monotonicity
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
        # Tuned weights for improved performance
        w_pos = 1.0
        w_empty = 3.0
        w_merge = 1.2
        w_mono = 1.5
        # Log-scale position score
        pos_score = math.log(features['position'], 2) if features['position'] > 0 else 0
        return (
            w_pos * pos_score +
            w_empty * features['empty'] +
            w_merge * features['merge'] +
            w_mono * features['monotonicity']
        )
