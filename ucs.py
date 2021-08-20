print("Imported ucs algorithm")

from game_env import GameEnv
from game_state import GameState

"""
ucs.py

TODO(alex): replace info below
Template file for you to implement your solution to Assignment 1.

This file should include a 'main' method, allowing this file to be executed as a program from the command line.

Your program should accept 3 command line arguments:
    1) input filename
    2) output filename
    3) mode (either 'ucs' or 'a_star')

COMP3702 2021 Assignment 1 Support Code

Last updated by njc 04/08/21
"""

# HELPER FUNCTIONS...


# MAIN FUNCTION...
# Args:
#     gamenv
# 
# Returns:
#     actions = [] (but filled with correct actions)
def ucs(game_env):
    
    # Read the input testcase file
    initial_state = game_env.get_init_state()

    actions = []

    # Do stuff
    print("Running ucs algorithm...")
    actions.append("wr")
    actions.append("wr")
    actions.append("wr")

    # Return the final list of actions
    return actions

if __name__ == '__main__':
    # main(sys.argv[1:])
    # Do stuff
    pass

