#!/usr/bin/env python3
import argparse
import importlib
import inspect
from game_2048 import Game2048

def play_one(agent):
    game = Game2048(mode="ai", algorithm=agent.get_action)
    while not game.is_game_over():
        move, *_ = agent.get_action(game)
        game.move_board(move)
        game.spawn_tile()
    return game.score, game.get_max_tile()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run 2048 with a chosen AI agent (no graphics)."
    )
    parser.add_argument(
        "--agent", 
        choices=["Random", "Greedy", "Expectimax", "SnakeExpectimax"], 
        default="Expectimax",
        help="Which agent to use"
    )
    parser.add_argument(
        "--depth", 
        type=int, 
        default=3,
        help="Expectimax search depth (only used if the agent supports it)"
    )
    parser.add_argument(
        "--games", 
        type=int, 
        default=10,
        help="How many full games to simulate"
    )
    args = parser.parse_args()

    # Dynamically import your agent class
    mod = importlib.import_module(f"ai_algs.{args.agent}_ai")
    AgentClass = getattr(mod, f"{args.agent}Agent")

    # Inspect __init__ to see if it accepts a depth parameter
    sig = inspect.signature(AgentClass.__init__)
    if "depth" in sig.parameters:
        agent = AgentClass(depth=args.depth)
    else:
        agent = AgentClass()

    scores = []
    tiles = []
    for i in range(1, args.games + 1):
        score, max_tile = play_one(agent)
        scores.append(score)
        tiles.append(max_tile)
        print(f"Game {i:2d}: score = {score:6d}   max tile = {max_tile}")

    avg_score = sum(scores) / len(scores)
    avg_tile  = sum(tiles)  / len(tiles)
    print("\nSummary over", args.games, "games:")
    print(f"  • Average score    = {avg_score:,.1f}")
    print(f"  • Average max tile = {avg_tile:.1f}")