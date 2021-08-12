import sys
import os

from game_env import GameEnv
from game_state import GameState

"""
solution.py

Template file for you to implement your solution to Assignment 1.

This file should include a 'main' method, allowing this file to be executed as a program from the command line.

Your program should accept 3 command line arguments:
    1) input filename
    2) output filename
    3) mode (either 'ucs' or 'a_star')

COMP3702 2021 Assignment 1 Support Code

Last updated by njc 04/08/21
"""


#
#
# Code for any classes or functions you need can go here.
#
#


def write_output_file(filename, actions):
    """
    Write a list of actions to an output file.
    :param filename: name of output file
    :param actions: list of actions where is action an element of GameEnv.ACTIONS
    """
    f = open(filename, 'w')
    for i in range(len(actions)):
        f.write(str(actions[i]))
        if i < len(actions) - 1:
            f.write(',')
    f.write('\n')
    f.close()


def main(arglist):
    if len(arglist) != 3:
        print("Running this file launches your solver.")
        print("Usage: play_game.py [input_filename] [output_filename] [mode = 'ucs' or 'a*']")

    input_file = arglist[0]
    output_file = arglist[1]
    mode = arglist[2]

    assert os.path.isfile(input_file), '/!\\ input file does not exist /!\\'
    assert mode == 'ucs' or mode == 'a_star', '/!\\ invalid mode argument /!\\'

    # Read the input testcase file
    game_env = GameEnv(input_file)
    initial_state = game_env.get_init_state()

    actions = []

    #
    #
    # Code for your main method can go here.
    #
    # Your code should find a sequence of actions for the agent to follow to reach the goal using the search type given
    # by 'mode', and store this sequence in 'actions'.
    #
    #

    # Write the solution to the output file
    write_output_file(output_file, actions)


if __name__ == '__main__':
    main(sys.argv[1:])

