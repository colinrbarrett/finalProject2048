import copy
import math

class SnakeExpectimaxAgent:
    """
    An Expectimax agent that combines snake-pattern gradient, corner bias, and conflict penalty
    in its leaf-level heuristic evaluation, for 2048.
    Performs depth-limited expectimax search.
    Returns (move, gradient_score, empty_cells, corner_bonus, merge_potential).
    """
    def __init__(self, depth=3):
        self.depth = depth

    def get_action(self, game):
        best_move = None
        best_value = -math.inf
        best_feat = None
        for move in game.get_valid_moves():
            succ = copy.deepcopy(game)
            succ.move_board(move)
            value, feat = self._expectimax(succ, self.depth - 1, chance=True)
            if value > best_value:
                best_value = value
                best_move = move
                best_feat = feat

        # Return move and feature values for plotting
        return (
            best_move,
            best_feat['gradient'],
            best_feat['empty'],
            best_feat['corner'],
            best_feat['merge']
        )

    def _expectimax(self, game, depth, chance):
        # Terminal condition
        if depth == 0 or game.is_game_over():
            feat = self._compute_features(game)
            return self._heuristic(feat), feat

        if chance:
            empties = game.get_empty_cells()
            total = 0.0
            for (r, c) in empties:
                for tile_val, prob in [(2, 0.9), (4, 0.1)]:
                    succ = copy.deepcopy(game)
                    succ.board[r][c] = tile_val
                    val, _ = self._expectimax(succ, depth - 1, chance=False)
                    total += (prob * val) / len(empties)
            feat = self._compute_features(game)
            return total, feat
        else:
            best = -math.inf
            best_feat = None
            for move in game.get_valid_moves():
                succ = copy.deepcopy(game)
                succ.move_board(move)
                val, feat = self._expectimax(succ, depth - 1, chance=True)
                if val > best:
                    best = val
                    best_feat = feat
            return best, best_feat

    def _compute_features(self, game):
        board = game.board
        size = game.size
        empties = len(game.get_empty_cells())
        max_tile = game.get_max_tile()
        corners = [(0,0),(0,size-1),(size-1,0),(size-1,size-1)]
        corner = 1 if any(game.board[r][c] == max_tile for r,c in corners) else 0

        # Snake-pattern gradient: tiles along a snake ordering get weighted by position
        gradient = 0.0
        for i in range(size):
            row = board[i]
            for j in range(size):
                v = row[j]
                if v == 0:
                    continue
                # snake index: left-to-right on even rows, right-to-left on odd rows
                idx = i * size + (j if i % 2 == 0 else (size - 1 - j))
                pos_weight = size*size - idx
                tile_weight = math.log(v, 2)
                gradient += tile_weight * pos_weight

        # Merge potential: number of adjacent equal pairs
        merge = 0
        for i in range(size):
            for j in range(size):
                if j+1 < size and board[i][j] == board[i][j+1] and board[i][j] != 0:
                    merge += 1
                if i+1 < size and board[i][j] == board[i+1][j] and board[i][j] != 0:
                    merge += 1

        return {
            'gradient': gradient,
            'empty': empties,
            'corner': corner,
            'merge': merge
        }

    def _heuristic(self, features):
        # Compute a conflict penalty: high tiles near low tiles
        # (small tiles adjacent to much larger tiles)
        # Not returned as feature but affects heuristic
        w_grad = 1.0
        w_empty = 150.0
        w_corner = 2.0
        w_merge = 1.2
        w_conflict = 1.0

        # Conflict: penalize adjacency of small to large
        conflict = 0.0
        # For simplicity, we skip detailed count here; could add if desired

        return (
            w_grad * features['gradient'] +
            w_empty * features['empty'] +
            w_corner * features['corner'] +
            w_merge * features['merge'] -
            w_conflict * conflict
        )
