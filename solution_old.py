import time
import random as random
import math as math

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
verbose = False
episodes = 0

# Initial Q Value
Q_INITIAL = 0  # -math.inf


class RLAgent:
    def __init__(self, game_env: GameEnv):
        """
        Constructor for your solver class.

        Any additional instance variables you require can be initialised here.

        Computationally expensive operations should not be included in the constructor, and should be placed in the
        plan_offline() method instead.

        This method has an allowed run time of 1 second, and will be terminated by the simulator if not completed within
        the limit.
        """

        # TODO: Initialise any instance variables you require here.
        self.game_env = game_env
        self.algorithm = "qlearning"

        if self.algorithm == "qlearning":
            # init a qlearning agent class
            self.solver = QLearningSolver(game_env)
            pass
        elif self.algorithm == "sarsa":
            # init a sarsa agent class
            pass
        else:
            raise ValueError

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
        # optional: loop for ensuring your code exits before exceeding the reward target or time limit
        while (self.game_env.get_total_reward() > self.game_env.training_reward_tgt) and \
                (time.time() - t0 < self.game_env.training_time - 1):

            # TODO: Code for training can go here

            # if iterations % 1000 == 0:
            #     print(f'Iteration {iterations}: ')
            #     self.solver.print_values_and_policy()
            #     print(f'Current State: {self.solver.persistent_state}.')
            #     _ = input("Press Enter to Continue...")
            #     print("")
            #     print("")
            #     pass

            if self.algorithm == "qlearning":
                # run qlearning training
                self.solver.next_iteration()

                # self.solver.print_values()
                # _ = input("Press Enter to Continue...")

                # if self.solver.persistent_state.gem_status == (1, 1):
                #     self.solver.print_agent_position()
                    # time.sleep(0.1)

            elif self.algorithm == "sarsa":
                # run sarsa training
                pass
            else:
                raise ValueError
            iterations = iterations + 1

        print(f'Completed {iterations} iterations (across {episodes} episodes) of training in'
              f' {round(time.time() - t0,1)} seconds.')
        self.solver.print_values_and_policy()

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

        # TODO: Code for selecting an action based on learned Q-values can go here

        if self.algorithm == "qlearning":
            # select action
            return self.solver.select_action(state)
        elif self.algorithm == "sarsa":
            # select action
            pass
        else:
            raise ValueError

    # TODO: Code for any additional methods you need can go here


class QLearningSolver:
    def __init__(self, game_env: GameEnv):
        """
        Constructor for the q-learning class.
        """
        self.game_env = game_env
        self.epsilon = 0.6
        self.alpha = 0.01  # OG learning rate 0.1, wanted reduce it to get more stale convergence
        self.discount = 0.9

        self.states = get_states(self.game_env)  # list of all possible states we can be in (includes lava,
        # but excludes walls - since you cant go inside a wall block)

        # self.persistent_state = random.choice(self.states)  # internal state used for training
        # self.persistent_state = GameState(1, 10, (1, 1))
        self.persistent_state = GameState(self.game_env.init_row, self.game_env.init_col, tuple(0 for g in self.game_env.gem_positions))
        print("###")
        print(f'STARTING STATE: {self.persistent_state}')
        print("###")
        print("")

        self.q_values = {}  # dict mapping (state, action) to float

    def next_iteration(self):
        global verbose
        global episodes

        # Check if we have an existing q value for this s,a pair - if we do, assign best_q and best_a to be
        # that, but otherwise if we haven't tried this s,a pair before, assign best_q = -INF and best_a = None
        best_q = Q_INITIAL
        best_a = None
        for a in self.game_env.ACTIONS:
            if ((self.persistent_state, a) in self.q_values.keys() and
                    self.q_values[(self.persistent_state, a)] > best_q):
                best_q = self.q_values[(self.persistent_state, a)]
                best_a = a

        while True:  # keep trying actions until we get a valid one we can update the q-value for
            # ===== Decide an action to try (either explore or exploit) =====
            random.seed(time.time())
            a = random.random()
            if best_a is None or a < self.epsilon:
                action = random.choice(list(self.game_env.ACTIONS))
            else:
                action = best_a
                print(f'State:  {self.persistent_state}, Best Action: {best_a}')

            # ===== Simulate result of action =====
            (action_is_valid, reward, next_state, state_is_terminal) = self.game_env.perform_action(
                self.persistent_state, action, seed=time.time())

            # If the action is legal, calculate the value of that action and update the q value for the s,a pair
            if action_is_valid:
                # ===== update value table =====
                # Q(s,a) <-- Q(s,a) + alpha * (temporal difference)
                # Q(s,a) <-- Q(s,a) + alpha * (target - Q(s, a))
                # target = r + gamma * max_{a' in A} Q(s', a')
                # compute target

                # Check if we have explored the next (successor) state and get its best action and q-value
                # If not explored, best action = None, best q value = -INF
                best_q1 = Q_INITIAL
                # best_a1 = None
                for a1 in self.game_env.ACTIONS:
                    if ((next_state, a1) in self.q_values.keys() and
                            self.q_values[(next_state, a1)] > best_q1):
                        best_q1 = self.q_values[(next_state, a1)]
                        # print((next_state, a1, self.q_values[(next_state, a1)]))
                        # best_a1 = a1
                if self.game_env.is_solved(next_state):
                    best_q1 = 0  # assign the goal state a 0 future reward
                elif self.game_env.is_game_over(next_state):
                    print("############################ DEATH ############################")
                    best_q1 = 0  # TODO: test

                # Calculate the target
                target = reward + (self.discount * best_q1)

                # Calculate the new q-value using TD (difference between old q-value and target)
                if ((self.persistent_state, action) in self.q_values) and \
                        (self.q_values[(self.persistent_state, action)] != -math.inf):
                    old_q = self.q_values[(self.persistent_state, action)]
                else:
                    old_q = 0
                self.q_values[(self.persistent_state, action)] = old_q + (self.alpha * (target - old_q))

                # print(self.q_values)

                # if not math.isnan(self.q_values[(self.persistent_state, action)]) and self.q_values[(
                #         self.persistent_state, action)] != -math.inf:
                # print(self.q_values[(self.persistent_state, action)])

                # move to next state
                if state_is_terminal:
                    # If we reached the exit dump the agent back in a random state to start and try again
                    random.seed(time.time())
                    # self.print_values()
                    # print(self.persistent_state)

                    # self.print_values()

                    self.persistent_state = random.choice(self.states)
                    self.persistent_state = GameState(self.game_env.init_row, self.game_env.init_col, tuple(0 for g in self.game_env.gem_positions))

                    print(f'____________ Starting new Episode at: {self.persistent_state} ____________')
                    print("")

                    if self.persistent_state.gem_status != (0, 0):
                        self.print_values_and_policy()
                        quit()

                    episodes = episodes + 1
                    # _ = input("Press Enter to Continue...")
                else:
                    # If we haven't reached the exit explore the next state
                    self.persistent_state = next_state

                # Break out of the while true loop
                break

            # If this action is impossible to execute from this state (i.e. jumping when already in the air),
            # then randomly pick another action to try

    def run_training(self, max_iterations):
        t0 = time.time()
        for i in range(max_iterations):
            self.next_iteration()
        print(f'Completed {max_iterations} iterations of training in {round(time.time() - t0, 1)} seconds.')
        print("")

    def select_action(self, state):
        # choose the action with the highest Q-value for the given state
        best_q = Q_INITIAL
        best_a = None
        for a in self.game_env.ACTIONS:
            if ((state, a) in self.q_values.keys() and
                    self.q_values[(state, a)] > best_q):
                best_q = self.q_values[(state, a)]
                best_a = a

        if best_a is None:
            best_a = random.choice(list(self.game_env.ACTIONS))
            # print(state)
            # print("No best action")
            return best_a
        else:
            # print(state)
            # print(best_a)
            return best_a

    def print_values_and_policy(self):
        # print()
        # print(self.q_values)
        # print()

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
                best_q = Q_INITIAL
                best_a = None
                for a in self.game_env.ACTIONS:
                    if ((state, a) in self.q_values.keys()) and (self.q_values[(state, a)] < best_q):
                        best_q = self.q_values[(state, a)]
                        best_a = a
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
                    line += str(round(v, 1))
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

    def print_values(self):
        gem_status = tuple(0 for g in self.game_env.gem_positions)

        values = [None] * self.game_env.n_rows
        for row in range(0, self.game_env.n_rows):
            values[row] = ['XXX'] * self.game_env.n_cols

        for state in self.states:
            if state.gem_status == gem_status:
                # Find the q value and policy for each state
                best_q = Q_INITIAL
                for a in self.game_env.ACTIONS:
                    if ((state, a) in self.q_values.keys()) and (self.q_values[(state, a)] > best_q):
                        best_q = self.q_values[(state, a)]
                values[state.row][state.col] = best_q

        print('========== Values ==========')
        for r in range(self.game_env.n_rows):
            row = values[r]
            line = '['
            for c in range(self.game_env.n_cols):
                v = row[c]
                if self.persistent_state.row == r and self.persistent_state.col == c:
                    # current tile is player
                    line += ' P '
                elif v != 'XXX':
                    line += str(round(v, 1))
                else:
                    line += 'XXX '
                line += ', '
            line += ']'
            print(line)

    def print_agent_position(self):
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


def get_states(game_env: GameEnv):
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

# def get_legal_actions(game_state: GameState, game_env: GameEnv):
#     states = []  # set up a list of all the possible game states
#     for row in range(0, game_env.n_rows):
#         for col in range(0, game_env.n_cols):
#             for gem_digits in range(0, int(math.pow(2, game_env.n_gems))):
#                 gem_string = bin(gem_digits)[2:].zfill(game_env.n_gems)
#                 gem_list = list(gem_string)
#
#                 for i in range(0, len(gem_list)):
#                     gem_list[i] = int(gem_list[i])
#
#                 gem_tuple = tuple(gem_list)
#                 state = GameState(row, col, gem_tuple)
#
#                 if game_env.grid_data[row][col] != game_env.SOLID_TILE:
#                     states.append(state)
#     return states