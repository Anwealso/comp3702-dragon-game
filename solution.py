import time

from game_env import GameEnv
from game_state import GameState

"""
solution.py

Template file for you to implement your solution to Assignment 3.

You must implement the following method stubs, which will be invoked by the simulator during testing:
    __init__(game_env)
    run_training()
    select_action()
    
To ensure compatibility with the autograder, please avoid using try-except blocks for Exception or OSError exception
types. Try-except blocks with concrete exception types other than OSError (e.g. try: ... except ValueError) are allowed.

COMP3702 2021 Assignment 3 Support Code

Last updated by njc 10/10/21
"""


class RLAgent:

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

    def run_training(self):
        """
        This method will be called once at the beginning of each episode.

        You can use this method to perform training (e.g. via Q-Learning or SARSA).

        The allowed run time for this method is given by 'game_env.training_time'. The method will be terminated by the
        simulator if it does not complete within this limit - you should design your algorithm to ensure this method
        exits before the time limit is exceeded.
        """
        t0 = time.time()

        #
        #
        # TODO: Code for training can go here
        #
        #

        # optional: loop for ensuring your code exits before exceeding the reward target or time limit
        while self.game_env.get_total_reward() > self.game_env.training_reward_tgt and \
                time.time() - t0 < self.game_env.training_time - 1:
            #
            #
            # TODO: Code for training can go here
            #
            #
            pass

    def select_action(self, state):
        """
        This method will be called each time the agent is called upon to decide which action to perform (once for each
        step of the episode).

        You can use this method to select an action based on the Q-value estimates learned during training.

        The allowed run time for this method is 1 second. The method will be terminated by the simulator if it does not
        complete within this limit - you should design your algorithm to ensure this method exits before the time limit
        is exceeded.

        :param state: the current state, a GameState instance
        :return: action, the selected action to be performed for the current state
        """

        #
        #
        # TODO: Code for selecting an action based on learned Q-values can go here
        #
        #


    #
    #
    # TODO: Code for any additional methods you need can go here
    #
    #

