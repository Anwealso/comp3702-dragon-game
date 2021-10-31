import time

from game_env import GameEnv
from game_state import GameState
import random as random
import math as math

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

episodes = 0

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
        global episodes
        t0 = time.time()
        iterations = 0

        #
        #
        # TODO: Code for training can go here
        #
        #

        # optional: loop for ensuring your code exits before exceeding the reward target or time limit
        # while self.game_env.get_total_reward() > self.game_env.training_reward_tgt and \
        #         time.time() - t0 < self.game_env.training_time - 1:
        # So we are still under time, but....
        # The first cond. = False, so therefore self.game_env.get_total_reward() <= self.game_env.training_reward_tgt
        while time.time() - t0 < self.game_env.training_time - 1 and iterations < 10000:
            #
            #
            # TODO: Code for training can go here
            #
            #
            print(f'ITERATION {iterations}:')
            self.agent.next_iteration()
            iterations = iterations + 1
            self.agent.print_values_and_policy()
            self.agent.print_agent_position()
            _ = input("Press enter to continue")

        print(f'Completed {iterations} iterations (across {episodes} episodes) of training in'
              f' {round(time.time() - t0,1)} seconds.')
        quit()

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
    ACTION_SEED = 456

    def __init__(self, game_env):
        self.game_env = game_env

        self.states = get_states(game_env)  # all possible states the agent can inhabit in the level

        self.persistent_state = get_initial_state(game_env)  # internal state used for training

        self.q_values = {}  # dict mapping (state, action) to float
        for state in self.states:
            for action in self.game_env.ACTIONS:
                self.q_values[(state, action)] = 0

    def next_iteration(self):
        global episodes
        print(f'Current state: {self.persistent_state}')

        # ===== select an action to perform (epsilon greedy exploration) =====
        best_q = -math.inf
        actions = get_legal_actions(self.game_env, self.persistent_state)  # legal actions from this state
        for a in actions:
            if ((self.persistent_state, a) in self.q_values.keys() and
                    self.q_values[(self.persistent_state, a)] > best_q):
                best_q = self.q_values[(self.persistent_state, a)]
                action = a
                print(f'Best action = {action}')
            elif ((self.persistent_state, a) not in self.q_values.keys() and
                    best_q < 0):
                # If this next state,action is unexplored: set best_q = 0 (encourages exploration)
                best_q = 0
                action = a
                print(f'Unexplored action = {action}')
        # epsilon chance to choose random action
        if random.random() < self.EPSILON:
            action = random.choice(actions)
            print(f'Random action = {action}')

        # ==========================================================================================
        # # If we are not in the exit state, get the best possible future reward
        # best_q1 = -math.inf
        # best_a1 = None
        # for a1 in actions:
        #     if ((next_state, a1) in self.q_values.keys() and
        #             self.q_values[(next_state, a1)] > best_q1):
        #         best_q1 = self.q_values[(next_state, a1)]
        #         best_a1 = a1
        #         print(f'- best_a1 = {a1}')
        #     elif ((next_state, a1) not in self.q_values.keys() and
        #             0 > best_q1):
        #         # If this next state,action is unexplored: set best_q1 = 0 (encourages exploration)
        #         best_q1 = 0
        #         best_a1 = a1
        #         print('- picking unexplored a1')
        # ==========================================================================================


        # ===== simulate result of action =====
        # next_state, reward = self.grid.apply_move(self.persistent_state, action)
        (action_is_valid, reward, next_state, state_is_terminal) = \
            self.game_env.perform_action(self.persistent_state, action, seed=self.ACTION_SEED)
        # NOTE: state_is_terminal == (is_game_over) or (is_solved)
        # NOTE: is_solved tells us if the NEXT state is the exit state
        # NOTE: is_game_over tells us if the NEXT state is the exit state
        # NOTE: no reward is given for going into the exit state (i.e. next_state = exit state)

        # ===== update value table =====
        # Q(s,a) <-- Q(s,a) + alpha * (temporal difference)
        # Q(s,a) <-- Q(s,a) + alpha * (target - Q(s, a))
        # target = r + gamma * max_{a' in A} Q(s', a')
        # compute target

        if state_is_terminal:
            # If we are moving into the exit state, there are no possible future rewards
            best_q1 = 0
        else:
            # If we are not in the exit state, get the best possible future reward
            best_q1 = -math.inf
            for a1 in actions:
                if ((next_state, a1) in self.q_values.keys() and
                        self.q_values[(next_state, a1)] > best_q1):
                    best_q1 = self.q_values[(next_state, a1)]
                    best_a1 = a1
                    print(f'- best_a1 = {best_a1}')
                elif ((next_state, a1) not in self.q_values.keys() and
                        best_q1 < 0):
                    # If this next state,action is unexplored: set best_q1 = 0 (encourages exploration)
                    best_q1 = 0
                    best_a1 = a1
                    print(f'- unexplored a1 = {best_a1}')

        target = reward + (self.DISCOUNT * best_q1)
        if (self.persistent_state, action) in self.q_values:
            old_q = self.q_values[(self.persistent_state, action)]
        else:
            old_q = 0
        self.q_values[(self.persistent_state, action)] = old_q + (self.ALPHA * (target - old_q))

        # Send the agent to a new state
        if self.persistent_state == get_exit_state(self.game_env):
            # go back to the starting state
            self.persistent_state = get_initial_state(self.game_env)
            episodes = episodes + 1
            print("EXIT")
            # quit()
        else:
            print("Moving to next state...")
            # move to next state
            self.persistent_state = next_state

    # def run_training(self, max_iterations):
    #     t0 = time.time()
    #     for i in range(max_iterations):
    #         self.next_iteration()
    #     print(f'Completed {max_iterations} iterations of training in {round(time.time() - t0, 1)} seconds.')

    def select_action(self, state):
        # choose the action with the highest Q-value for the given state
        best_q = -math.inf
        best_a = None
        actions = get_legal_actions(self.game_env, self.persistent_state)
        for a in actions:
            if ((state, a) in self.q_values.keys() and
                    self.q_values[(state, a)] > best_q):
                best_q = self.q_values[(state, a)]
                best_a = a

        if best_a is None:
            return random.choice(actions)
        else:
            return best_a

    def print_values_and_policy(self):
        gem_status = tuple(0 for g in self.game_env.gem_positions)
        # gem_status = self.persistent_state.gem_status

        values = [None] * self.game_env.n_rows
        for row in range(0, self.game_env.n_rows):
            values[row] = ['XXX'] * self.game_env.n_cols

        policy = [None] * self.game_env.n_rows
        for row in range(0, self.game_env.n_rows):
            policy[row] = ['XXX'] * self.game_env.n_cols

        for state in self.states:
            if state.gem_status == gem_status:
                # Find the q value and policy for each state
                best_q = -math.inf
                best_a = None
                for a in self.game_env.ACTIONS:
                    if ((state, a) in self.q_values.keys()) and (self.q_values[(state, a)] > best_q):
                        best_q = self.q_values[(state, a)]
                        best_a = a
                        print(best_q)
                if best_q == 0:
                    best_a = None
                values[state.row][state.col] = best_q
                policy[state.row][state.col] = best_a

        # print(self.states)
        # print()
        print(self.q_values)
        print()
        print(values)

        print('========== Values ==========')
        for row in values:
            line = '['
            for i, v in enumerate(row):
                if v != 'XXX':
                    line += ' '
                    line += str(round(v, 1))
                    line += '  '
                else:
                    line += 'XXX '
                line += ', '
            line += ']'
            print(line)
        print('')
        print('========== Policy ==========')
        action_emoji = {'j': "▲ ", 'wr': "► ", 'wl': "◄ ", 'gr1': "↘1", 'gr2': "↘2", 'gr3': "↘3",
                        'gl1': "↙1", 'gl2': "↙2", 'gl3': "↙3", 'd1': "▼ ", 'd2': "▼ ", 'd3': "▼ "}

        for row, row_list in enumerate(policy):
            line = ''
            for col, p in enumerate(row_list):
                if (row, col) in self.game_env.gem_positions and (p is None):
                    # current tile is gem
                    line += " G "
                elif (p != "XXX") and (p is not None):
                    line += ' ' + action_emoji[p] + ''
                elif p == "XXX":
                    line += 'XXX'
                else:
                    line += '   '
                line += ''
            # line += ''
            print(line)
        print('')

    def print_agent_position(self):
        print('========== Agent Position ==========')
        game_env = self.game_env
        state = self.persistent_state
        for r in range(game_env.n_rows):
            line = ''
            for c in range(game_env.n_cols):
                if state.row == r and state.col == c:
                    # current tile is player
                    line += game_env.grid_data[r][c] + 'P' + game_env.grid_data[r][c]
                elif game_env.exit_row == r and game_env.exit_col == c:
                    # current tile is exit
                    line += game_env.grid_data[r][c] + 'E' + game_env.grid_data[r][c]
                elif (r, c) in game_env.gem_positions and \
                        state.gem_status[game_env.gem_positions.index((r, c))] == 0:
                    # current tile is an uncollected gem
                    line += game_env.grid_data[r][c] + 'G' + game_env.grid_data[r][c]
                elif game_env.grid_data[r][c] in {game_env.SUPER_CHARGE_TILE, game_env.SUPER_JUMP_TILE}:
                    line += '[' + game_env.grid_data[r][c] + ']'
                else:
                    line += game_env.grid_data[r][c] * 3
            print(line)
        print('\n' * 2)

def get_initial_state(game_env: GameEnv):
    """
    Gets the initial agent state (starting position and gem_status) in the game_env for this level

    :param game_env: the game environment for the current map the agent is solving
    :return: the initial game_state
    """
    return GameState(game_env.init_row, game_env.init_col, tuple(0 for _ in game_env.gem_positions))


def get_exit_state(game_env: GameEnv):
    """
    Gets the exit state in the game_env for this level

    :param game_env: the game environment for the current map the agent is solving
    :return: the exit game_state
    """
    return GameState(game_env.exit_row, game_env.exit_col, tuple(1 for _ in game_env.gem_positions))


def get_states(game_env: GameEnv):
    """
    Get a list of all the possible states the agent can occupy (see list below)
        - agent CAN occupy the exit state, lava tiles, any permeable tiles like gems, air or ladder tiles;
        - agent CANNOT occupy any solid tiles like wall tile and super charge and jump blocks

    :param game_env: the game environment for the current map the agent is solving
    :return: a list of all the possible states the agent can occupy
    """
    states = []  # set up a list of all the possible game states
    for row in range(0, game_env.n_rows):
        for col in range(0, game_env.n_cols):
            for gem_digits in range(0, int(math.pow(2, game_env.n_gems))):
                gem_string = bin(gem_digits)[2:].zfill(game_env.n_gems)
                gem_list = list(gem_string)

                for i in range(0, len(gem_list)):
                    gem_list[i] = int(gem_list[i])

                gem_tuple = tuple(gem_list)
                state = GameState(row, col, gem_tuple)

                if game_env.grid_data[row][col] != game_env.SOLID_TILE:
                    states.append(state)
    return states


def get_legal_actions(game_env: GameEnv, state: GameState):
    legal_actions = []

    for action in game_env.ACTIONS:
        # check if the given action is valid for the given state
        if action in {game_env.WALK_LEFT, game_env.WALK_RIGHT, game_env.JUMP}:
            # check walkable ground prerequisite if action is walk or jump
            if game_env.grid_data[state.row + 1][state.col] in game_env.WALK_JUMP_ALLOWED_TILES:
                # prerequisite is satisfied
                legal_actions.append(action)
        else:
            # check permeable ground prerequisite if action is glide or drop
            if game_env.grid_data[state.row + 1][state.col] in game_env.GLIDE_DROP_ALLOWED_TILES:
                # prerequisite is satisfied
                legal_actions.append(action)

    return legal_actions
