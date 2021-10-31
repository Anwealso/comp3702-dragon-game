import time

from game_env import GameEnv
from game_state import GameState
import random as random

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

        self.agent = QLearningAgent(game_env)

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
            self.agent.next_iteration()

        self.agent.print_values_and_policy()

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
        self.agent.select_action(state)

    #
    #
    # TODO: Code for any additional methods you need can go here
    #
    #


class QLearningAgent:
    EPSILON = 0.4
    ALPHA = 0.1
    DISCOUNT = 0.9

    def __init__(self, game_env):
        self.game_env = game_env

        self.states = [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2)]

        self.persistent_state = random.choice(self.states)  # internal state used for training

        self.q_values = {}  # dict mapping (state, action) to float

    def next_iteration(self):
        # ===== select an action to perform (epsilon greedy exploration) =====
        best_q = -math.inf
        best_a = None
        for a in ACTIONS:
            if ((self.persistent_state, a) in self.q_values.keys() and
                    self.q_values[(self.persistent_state, a)] > best_q):
                best_q = self.q_values[(self.persistent_state, a)]
                best_a = a

        # epsilon chance to choose random action
        if best_a is None or random.random() < self.EPSILON:
            action = random.choice(ACTIONS)
        else:
            action = best_a

        # ===== simulate result of action =====
        next_state, reward = self.grid.apply_move(self.persistent_state, action)

        # ===== update value table =====
        # Q(s,a) <-- Q(s,a) + alpha * (temporal difference)
        # Q(s,a) <-- Q(s,a) + alpha * (target - Q(s, a))
        # target = r + gamma * max_{a' in A} Q(s', a')
        # compute target
        best_q1 = -math.inf
        best_a1 = None
        for a1 in ACTIONS:
            if ((next_state, a1) in self.q_values.keys() and
                    self.q_values[(next_state, a1)] > best_q1):
                best_q1 = self.q_values[(next_state, a1)]
                best_a1 = a1
        if best_a1 is None or next_state == EXIT_STATE:
            best_q1 = 0
        target = reward + (self.grid.discount * best_q1)
        if (self.persistent_state, action) in self.q_values:
            old_q = self.q_values[(self.persistent_state, action)]
        else:
            old_q = 0
        self.q_values[(self.persistent_state, action)] = old_q + (self.ALPHA * (target - old_q))

        # move to next state
        self.persistent_state = next_state

    def run_training(self, max_iterations):
        t0 = time.time()
        for i in range(max_iterations):
            self.next_iteration()
        print(f'Completed {max_iterations} iterations of training in {round(time.time() - t0, 1)} seconds.')

    def select_action(self, state):
        # choose the action with the highest Q-value for the given state
        best_q = -math.inf
        best_a = None
        for a in ACTIONS:
            if ((state, a) in self.q_values.keys() and
                    self.q_values[(state, a)] > best_q):
                best_q = self.q_values[(state, a)]
                best_a = a

        if best_a is None:
            return random.choice(ACTIONS)
        else:
            return best_a

    def print_values_and_policy(self):
        values = [[0, 0, 0, 0], [0, 'N/A', 0, 0], [0, 0, 0, 0]]
        policy = [['_', '_', '_', '_'], ['_', 'N/A', '_', '_'], ['_', '_', '_', '_']]
        for state in self.grid.states:
            best_q = -math.inf
            best_a = None
            for a in ACTIONS:
                if ((state, a) in self.q_values.keys() and
                        self.q_values[(state, a)] > best_q):
                    best_q = self.q_values[(state, a)]
                    best_a = a
            x, y = state
            values[y][x] = best_q
            policy[y][x] = best_a
        print('========== Values ==========')
        for row in reversed(values):
            line = '['
            for i, v in enumerate(row):
                if v != 'N/A':
                    line += str(round(v, 3))
                else:
                    line += 'N/A '
                if i != 3:
                    line += ', '
            line += ']'
            print(line)
        print('')
        print('========== Policy ==========')
        for row in reversed(policy):
            line = '['
            for i, p in enumerate(row):
                if p != 'N/A':
                    line += ' ' + ACTIONS_NAMES[p] + ' '
                else:
                    line += 'N/A'
                if i != 3:
                    line += ', '
            line += ']'
            print(line)
