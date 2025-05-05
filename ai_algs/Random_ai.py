import random
from game_2048 import Game2048

class RandomAgent:

    def get_action(self, game_state: Game2048):
        return random.choice(["Up", "Down", "Left", "Right"]), 0, 0, 0, 0