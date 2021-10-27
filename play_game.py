import sys
import time
import platform
import random
import hashlib

from game_env import GameEnv

if platform.system() != 'Windows':
    SEPARATOR = '/'
else:
    SEPARATOR = '\\'

"""
play_game.py

Running this file launches an interactive game session. Becoming familiar with the game mechanics may be helpful in
designing your solution.

The script takes 2 arguments:
- input_filename, which must be a valid testcase file (e.g. one of the provided files in the testcases directory)
- (optional) output_filename, which should be an unused .txt filename

If an output filename is provided, the sequence of actions you perform will be saved as an output file.

When prompted for an action, type one of the available action strings (e.g. wr, wl, etc) and press enter to perform the
entered action.

COMP3702 2021 Assignment 3 Support Code

Last updated by njc 10/10/21
"""


def stable_hash(x):
    return hashlib.md5(str(x).encode('utf-8')).hexdigest()


def main(arglist):
    if len(arglist) != 1:
        print("Running this file launches an interactive game session.")
        print("Usage: play_game.py [input_filename]")
        return -1

    input_file = arglist[0]
    init_seed = stable_hash(input_file.split(SEPARATOR)[-1])
    random.seed(init_seed)
    game_env = GameEnv(input_file)
    persistent_state = game_env.get_init_state()
    total_reward = 0

    # run simulation
    while True:
        game_env.render(persistent_state)
        print('Choose an action (wl, wr, j, gl1, gl2, gl3, gr1, gr2, gr3, d1, d2, d3, q[quit])')
        a = input().strip()
        if 'q' in a:
            print('Quitting.')
            break
        if a not in GameEnv.ACTIONS:
            print('Unrecognised action. Choose again.')
            continue
        valid, reward, new_state, terminal = game_env.perform_action(persistent_state, a, time.time())
        if not valid:
            print('Action is invalid for the current state. Choose again.')
            continue
        else:
            persistent_state = new_state
        print(f'Received reward: {reward}')
        total_reward += reward
        if terminal:
            print(f'Level completed with total reward of {round(total_reward, 1)} '
                  f'(benchmark reward = {game_env.eval_reward_tgt})')
            break


if __name__ == '__main__':
    main(sys.argv[1:])
