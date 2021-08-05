import sys

from game_env import GameEnv
from solution import write_output_file

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

COMP3702 2021 Assignment 1 Support Code

Last updated by njc 28/07/21
"""


def main(arglist):
    if len(arglist) != 1 and len(arglist) != 2:
        print("Running this file launches an interactive game session.")
        print("Usage: play_game.py [input_filename] (optional)[output_filename]")
        return -1

    input_file = arglist[0]
    if len(arglist) > 1:
        output_file = arglist[1]
    else:
        output_file = None

    game_env = GameEnv(input_file)
    persistent_state = game_env.get_init_state()
    actions = []
    total_cost = 0

    # run simulation
    while True:
        game_env.render(persistent_state)
        print('Choose an action (wl, wr, j, gl1, gl2, gl3, gr1, gr2, gr3, d1, d2, d3, q[quit])')
        a = input().strip()
        if 'q' in a:
            print('Quitting.')
            break
        if a not in GameEnv.ACTIONS:
            print('Invalid action. Choose again.')
            continue
        actions.append(a)
        total_cost += game_env.ACTION_COST[a]
        success, persistent_state = game_env.perform_action(persistent_state, a)
        if not success:
            print('Collision occurred.')
        if game_env.is_solved(persistent_state):
            game_env.render(persistent_state)
            print(f'Level completed with total cost of {round(total_cost, 1)}!')
            break
        elif game_env.is_game_over(persistent_state):
            game_env.render(persistent_state)
            print(f'Game Over. total cost = {round(total_cost, 1)}')
            break

    # write actions to output file
    if output_file is not None and len(actions) > 0:
        write_output_file(output_file, actions)
    return 0


if __name__ == '__main__':
    main(sys.argv[1:])
