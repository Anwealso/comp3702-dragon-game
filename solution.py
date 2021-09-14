import time

from game_env import GameEnv
from game_state import GameState

"""
solution.py

Template file for you to implement your solution to Assignment 2.

You must implement the following method stubs, which will be invoked by the simulator during testing:
    __init__(game_env)
    plan_offline()
    select_action()
    
To ensure compatibility with the autograder, please avoid using try-except blocks for Exception or OSError exception
types. Try-except blocks with concrete exception types other than OSError (e.g. try: ... except ValueError) are allowed.

COMP3702 2021 Assignment 2 Support Code

Last updated by njc 02/09/21
"""


class Solver:

    def __init__(self, game_env):
        """
        Constructor for your solver class.

        Any additional instance variables you require can be initialised here.

        Computationally expensive operations should not be included in the constructor, and should be placed in the
        plan_offline() method instead.

        This method has an allowed run time of 1 second, and will be terminated by the simulator if not completed within
        the limit.
        """
        self.game_env = game_env

        #
        #
        # TODO: Initialise any instance variables you require here.
        #
        #

    def plan_offline(self):
        """
        This method will be called once at the beginning of each episode.

        You can use this method to perform value iteration and/or policy iteration and store the computed policy, or
        (optionally) to perform pre-processing for MCTS.

        This planning should not depend on the initial state, as during simulation this is not guaranteed to match the
        initial position listed in the input file (i.e. you may be given a different position to the initial position
        when select_action is called).

        The allowed run time for this method is given by 'game_env.offline_time'. The method will be terminated by the
        simulator if it does not complete within this limit - you should design your algorithm to ensure this method
        exits before the time limit is exceeded.
        """
        t0 = time.time()

        #
        #
        # TODO: Code for offline planning can go here
        #
        #

        # optional: loop for ensuring your code exits before the time limit
        while time.time() - t0 < self.game_env.offline_time:
            #
            #
            # TODO: Code for offline planning can go here
            #
            #
            pass

    def select_action(self, state):
        """
        This method will be called each time the agent is called upon to decide which action to perform (once for each
        step of the episode).

        You can use this to retrieve the optimal action for the current state from a stored offline policy (e.g. from
        value iteration or policy iteration), or to perform MCTS simulations from the current state.

        The allowed run time for this method is given by 'game_env.online_time'. The method will be terminated by the
        simulator if it does not complete within this limit - you should design your algorithm to ensure this method
        exits before the time limit is exceeded.

        :param state: the current state, a GameState instance
        :return: action, the selected action to be performed for the current state
        """
        t0 = time.time()

        #
        #
        # TODO: Code for retrieving an action from an offline policy, or for online planning can go here
        #
        #

        # optional: loop for ensuring your code exits before the time limit
        while time.time() - t0 < self.game_env.offline_time:
            #
            #
            # TODO: Code for retrieving an action from an offline policy, or for online planning can go here
            #
            #
            pass

    #
    #
    # TODO: Code for any additional methods you need can go here
    #
    #

