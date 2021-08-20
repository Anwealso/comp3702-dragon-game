print("Imported ucs algorithm")

from game_env import GameEnv
from game_state import GameState

"""
ucs.py

TODO(alex): replace info below
A file to hold all the ucs function and all of its supporting methods needed to 
implement ucs search

This file should be imported into the solution.py file and have its ucs() 
function called from within solution.py

COMP3702 2021 Assignment 1 Code
"""

# ---------------------------------------------------------------------------- #
#                               HELPER FUNCTIONS                               #
# ---------------------------------------------------------------------------- #

# ...

# ...


# ---------------------------------------------------------------------------- #
#                                 MAIN FUNCTION                                #
# ---------------------------------------------------------------------------- #

# Runs the ucs algorithm on the given game_env and returns an optimised list of 
# actions to get the player through the course
# 
# Args:
#     gam_env: an object of class GameEnv, representing the state of the game
# 
# Returns:
#     actions: a list of moves, e.g. ['wr', 'j', 'gl2']
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
    # Do stuff
    pass

