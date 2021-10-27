import random
import hashlib
from game_state import GameState

"""
game_env.py

This file contains a class representing an Untitled Dragon Game environment. You should make use of this class in your
solver.

COMP3702 2021 Assignment 3 Support Code

Last updated by njc 25/10/21
"""


class GameEnv:
    """
    Instance of an Untitled Dragon Game environment. Stores the dimensions of the environment, initial player position,
    exit position, number of gems and position of each gem, time limit, cost target, the tile type of each grid
    position, and a list of all available actions.

    The grid is indexed top to bottom, left to right (i.e. the top left corner has coordinates (0, 0) and the bottom
    right corner has coordinates (n_rows-1, n_cols-1)).

    You may use and modify this class however you want.

    *** Note that evaluation on GradeScope will use an unmodified GameEnv instance as a simulator - unlike previous
    assignments, this rule will be in effect for assignment 3 ***
    """

    # input file symbols
    SOLID_TILE = 'X'
    LADDER_TILE = '='
    AIR_TILE = ' '
    LAVA_TILE = '*'
    SUPER_JUMP_TILE = 'J'
    SUPER_CHARGE_TILE = 'C'
    GEM_TILE = 'G'
    EXIT_TILE = 'E'
    PLAYER_TILE = 'P'
    VALID_TILES = {SOLID_TILE, LADDER_TILE, AIR_TILE, LAVA_TILE, SUPER_JUMP_TILE, SUPER_CHARGE_TILE, GEM_TILE,
                   EXIT_TILE, PLAYER_TILE}
    WALK_JUMP_ALLOWED_TILES = {SOLID_TILE, LADDER_TILE, SUPER_JUMP_TILE, SUPER_CHARGE_TILE}
    GLIDE_DROP_ALLOWED_TILES = {AIR_TILE, LADDER_TILE, LAVA_TILE}
    COLLISION_TILES = {SOLID_TILE, SUPER_JUMP_TILE, SUPER_CHARGE_TILE}

    # action symbols (i.e. output file symbols)
    WALK_LEFT = 'wl'
    WALK_RIGHT = 'wr'
    JUMP = 'j'
    GLIDE_LEFT_1 = 'gl1'
    GLIDE_LEFT_2 = 'gl2'
    GLIDE_LEFT_3 = 'gl3'
    GLIDE_RIGHT_1 = 'gr1'
    GLIDE_RIGHT_2 = 'gr2'
    GLIDE_RIGHT_3 = 'gr3'
    DROP_1 = 'd1'
    DROP_2 = 'd2'
    DROP_3 = 'd3'
    ACTIONS = {WALK_LEFT, WALK_RIGHT, JUMP, GLIDE_LEFT_1, GLIDE_LEFT_2, GLIDE_LEFT_3,
               GLIDE_RIGHT_1, GLIDE_RIGHT_2, GLIDE_RIGHT_3, DROP_1, DROP_2, DROP_3}
    WALK_ACTIONS = {WALK_LEFT, WALK_RIGHT}
    WALK_AND_JUMP_ACTIONS = {WALK_LEFT, WALK_RIGHT, JUMP}
    GLIDE_ACTIONS = {GLIDE_LEFT_1, GLIDE_LEFT_2, GLIDE_LEFT_3, GLIDE_RIGHT_1, GLIDE_RIGHT_2, GLIDE_RIGHT_3}
    DROP_ACTIONS = {DROP_1, DROP_2, DROP_3}
    GLIDE_AND_DROP_ACTIONS = {GLIDE_LEFT_1, GLIDE_LEFT_2, GLIDE_LEFT_3, GLIDE_RIGHT_1, GLIDE_RIGHT_2, GLIDE_RIGHT_3,
                              DROP_1, DROP_2, DROP_3}
    MAX_ACTION_COST = {WALK_LEFT: 1.0, WALK_RIGHT: 1.0, JUMP: 2.0,
                       GLIDE_LEFT_1: 0.7, GLIDE_LEFT_2: 1.0, GLIDE_LEFT_3: 1.2,
                       GLIDE_RIGHT_1: 0.7, GLIDE_RIGHT_2: 1.0, GLIDE_RIGHT_3: 1.2,
                       DROP_1: 0.3, DROP_2: 0.4, DROP_3: 0.5}
    MAX_COLLISION_PENALTY = 5
    MAX_GAME_OVER_PENALTY = 500

    @staticmethod
    def __stable_hash(x):
        return hashlib.md5(str(x).encode('utf-8')).hexdigest()

    @staticmethod
    def __get_random_prob_dist(keys):
        tmp_list = [random.random() for _ in range(len(keys))]
        tmp_total = sum(tmp_list)
        tmp_probs = [x / tmp_total for x in tmp_list]
        return {j: tmp_probs[i] for (i, j) in enumerate(keys)}

    def __init__(self, filename):
        """
        Process the given input file and create a new game environment instance based on the input file.
        :param filename: name of input file
        """
        self.filename = filename
        if '/' in filename:
            self.SEPARATOR = '/'
        else:
            self.SEPARATOR = '\\'
        f = open(filename, 'r')

        # ========== parse input file ==========
        grid_data = []
        i = 0
        for line in f:
            # skip annotations in input file
            if line.strip()[0] == '#':
                continue

            if i == 0:
                try:
                    self.n_rows, self.n_cols = tuple([int(x) for x in line.strip().split(',')])
                except ValueError:
                    assert False, f'!!! Invalid input file - n_rows and n_cols (line {i}) !!!'
            elif i == 1:
                try:
                    self.training_time = float(line.strip())
                except ValueError:
                    assert False, f'!!! Invalid input file - training time (line {i}) !!!'
            elif i == 2:
                try:
                    self.training_reward_tgt = float(line.strip())
                except ValueError:
                    assert False, f'!!! Invalid input file - training reward target (line {i}) !!!'
            elif i == 3:
                try:
                    self.eval_reward_tgt = float(line.strip())
                except ValueError:
                    assert False, f'!!! Invalid input file - evaluation reward target (line {i}) !!!'
            elif len(line.strip()) > 0:
                grid_data.append(list(line.strip()))
                assert len(grid_data[-1]) == self.n_cols,\
                    f'!!! Invalid input file - incorrect map row length (line {i}) !!!'

            i += 1

        # ========== extract gem, exit and initial positions ==========
        gem_positions = []
        self.init_row, self.init_col = None, None
        self.exit_row, self.exit_col = None, None
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if grid_data[r][c] == self.PLAYER_TILE:
                    assert self.init_row is None and self.init_col is None, \
                        '!!! Invalid input file - more than one initial player position !!!'
                    self.init_row, self.init_col = r, c
                    # assume player starts on air tile
                    grid_data[r][c] = self.AIR_TILE
                elif grid_data[r][c] == 'E':
                    assert self.exit_row is None and self.exit_col is None, \
                        '!!! Invalid input file - more than one exit position !!!'
                    self.exit_row, self.exit_col = r, c
                    # assume exit is placed on air tile
                    grid_data[r][c] = self.AIR_TILE
                elif grid_data[r][c] == self.GEM_TILE:
                    gem_positions.append((r, c))
                    # assume all gems are placed on air tiles
                    grid_data[r][c] = self.AIR_TILE
        self.n_gems = len(gem_positions)
        assert self.init_row is not None and self.init_col is not None, \
            '!!! Invalid input file - No player initial position !!!'
        assert self.exit_row is not None and self.exit_col is not None, \
            '!!! Invalid input file - No exit position !!!'

        assert len(grid_data) == self.n_rows, f'!!! Invalid input file - incorrect number of map rows !!!'

        self.gem_positions = gem_positions
        self.grid_data = grid_data

        # ========== generate random t_model, r_model ==========
        init_seed = self.__stable_hash(filename.split(self.SEPARATOR)[-1])
        random.seed(init_seed)

        # transition - glide probs (1-3), supercharge probs, superjump probs, ladder fall prob
        self.__glide1_probs = self.__get_random_prob_dist([0, 1, 2])
        self.__glide2_probs = self.__get_random_prob_dist([1, 2, 3])
        self.__glide3_probs = self.__get_random_prob_dist([2, 3, 4])
        self.__super_jump_probs = self.__get_random_prob_dist([2, 3, 4, 5])
        self.__super_charge_probs = self.__get_random_prob_dist([2, 3, 4, 5])
        self.__ladder_fall_prob = ((1 + 9 * random.random()) / 10)

        # reward - action_costs, collision_penalty, game_over_penalty
        self.__action_cost = {k: ((1 + random.random()) / 2) * v for (k, v) in self.MAX_ACTION_COST.items()}
        self.__collision_penalty = ((1 + 19 * random.random()) / 20) * self.MAX_COLLISION_PENALTY
        self.__game_over_penalty = ((1 + 4 * random.random()) / 5) * self.MAX_GAME_OVER_PENALTY

        # ========== keep track of total reward experienced ==========
        self.__reward_total = 0

    def get_init_state(self):
        """
        Get a state representation instance for the initial state.
        :return: initial state
        """
        return GameState(self.init_row, self.init_col, tuple(0 for g in self.gem_positions))

    def __check_collision_or_terminal(self, row, col, reward, row_move_dir, col_move_dir):
        terminal = False
        collision = False
        # check for collision condition
        if (not 0 <= row < self.n_rows) or (not 0 <= col < self.n_cols) or \
                self.grid_data[row][col] in self.COLLISION_TILES:
            reward -= self.__collision_penalty
            row -= row_move_dir     # bounce back to previous position
            col -= col_move_dir     # bounce back to previous position
            collision = True
        # check for game over condition
        elif self.grid_data[row][col] == self.LAVA_TILE:
            reward -= self.__game_over_penalty
            terminal = True

        return row, col, reward, collision, terminal

    def __check_collision_or_terminal_glide(self, row, col, reward, row_move_dir, col_move_dir):
        # variant for checking glide actions - checks row above as well as current row
        terminal = False
        collision = False
        # check for collision condition
        if (not 0 <= row < self.n_rows) or (not 0 <= col < self.n_cols) or \
                self.grid_data[row][col] in self.COLLISION_TILES or \
                self.grid_data[row - 1][col] in self.COLLISION_TILES:
            reward -= self.__collision_penalty
            row -= row_move_dir     # bounce back to previous position
            col -= col_move_dir     # bounce back to previous position
            collision = True
        # check for game over condition
        if self.grid_data[row][col] == self.LAVA_TILE or self.grid_data[row - 1][col] == self.LAVA_TILE:
            reward -= self.__game_over_penalty
            terminal = True

        return row, col, reward, collision, terminal

    def __check_gem_collected_or_goal_reached(self, row, col, gem_status):
        is_terminal = False
        # check if a gem is collected (only do this for final position of charge)
        if (row, col) in self.gem_positions and \
                gem_status[self.gem_positions.index((row, col))] == 0:
            gem_status = list(gem_status)
            gem_status[self.gem_positions.index((row, col))] = 1
            gem_status = tuple(gem_status)
        # check for goal reached condition (only do this for final position of charge)
        elif row == self.exit_row and col == self.exit_col and \
                all(gs == 1 for gs in gem_status):
            is_terminal = True
        return gem_status, is_terminal

    @staticmethod
    def __sample_move_dist(probs):
        rn = random.random()
        cumulative_prob = 0
        move_dist = 0
        for k in probs.keys():
            cumulative_prob += probs[k]
            if rn < cumulative_prob:
                move_dist = k
                break
        return move_dist

    def perform_action(self, state, action, seed=None):
        """
        Perform the given action on the given state, sample an outcome, and return whether the action was valid, and if
        so, the received reward, the resulting new state and whether the new state is terminal.
        :param state: current GameState
        :param action: an element of self.ACTIONS
        :param seed: random number generator seed (for consistent outcomes between runs)
        :return: (action_is_valid [True/False], received_reward [float], next_state [GameState],
                    state_is_terminal [True/False])
        """
        reward = -1 * self.MAX_ACTION_COST[action]
        is_game_over = False

        # check if the given action is valid for the given state
        if action in {self.WALK_LEFT, self.WALK_RIGHT, self.JUMP}:
            # check walkable ground prerequisite if action is walk or jump
            if self.grid_data[state.row + 1][state.col] not in self.WALK_JUMP_ALLOWED_TILES:
                # prerequisite not satisfied
                return False, None, None, None
        else:
            # check permeable ground prerequisite if action is glide or drop
            if self.grid_data[state.row + 1][state.col] not in self.GLIDE_DROP_ALLOWED_TILES:
                # prerequisite not satisfied
                return False, None, None, None

        # handle each action type separately
        if action in self.WALK_ACTIONS:
            if self.grid_data[state.row + 1][state.col] == self.SUPER_CHARGE_TILE:
                # sample a random move distance
                random.seed(seed)
                move_dist = self.__sample_move_dist(self.__super_charge_probs)

                # set movement direction
                if action == self.WALK_LEFT:
                    move_dir = -1
                else:
                    move_dir = 1

                next_row, next_col = state.row, state.col
                next_gem_status = state.gem_status

                # move up to the last adjoining supercharge tile
                while self.grid_data[next_row + 1][next_col + move_dir] == self.SUPER_CHARGE_TILE:
                    next_col += move_dir
                    # check for collision or game over
                    next_row, next_col, reward, collision, is_game_over = \
                        self.__check_collision_or_terminal(next_row, next_col, reward,
                                                           row_move_dir=0, col_move_dir=move_dir)
                    if collision or is_game_over:
                        break

                # move sampled move distance beyond the last adjoining supercharge tile
                for d in range(move_dist):
                    next_col += move_dir
                    # check for collision or game over
                    next_row, next_col, reward, collision, is_game_over = \
                        self.__check_collision_or_terminal(next_row, next_col, reward,
                                                           row_move_dir=0, col_move_dir=move_dir)
                    if collision or is_game_over:
                        break

                # check if a gem is collected or goal is reached (only do this for final position of charge)
                next_gem_status, is_solved = self.__check_gem_collected_or_goal_reached(next_row, next_col,
                                                                                        next_gem_status)

                self.__reward_total += reward
                return True, reward, GameState(next_row, next_col, next_gem_status), is_game_over or is_solved
            else:
                # if on ladder, sample whether fall occurs
                random.seed(seed)
                if self.grid_data[state.row + 1][state.col] == self.LADDER_TILE and \
                        self.grid_data[state.row + 2][state.col] not in self.COLLISION_TILES and \
                        random.random() < self.__ladder_fall_prob:
                    next_row, next_col = state.row + 2, state.col
                    row_move_dir = 1
                    col_move_dir = 0
                # not on ladder or no fall - set movement direction based on chosen action
                elif action == self.WALK_LEFT:
                    col_move_dir = -1
                    row_move_dir = 0
                    next_row, next_col = (state.row, state.col + col_move_dir)
                else:
                    col_move_dir = 1
                    row_move_dir = 0
                    next_row, next_col = (state.row, state.col + col_move_dir)
                next_gem_status = state.gem_status
                # check for collision or game over
                next_row, next_col, reward, collision, is_game_over = \
                    self.__check_collision_or_terminal(next_row, next_col, reward,
                                                       row_move_dir=row_move_dir, col_move_dir=col_move_dir)
                # check if a gem is collected or goal is reached
                next_gem_status, is_solved = self.__check_gem_collected_or_goal_reached(next_row, next_col,
                                                                                        next_gem_status)

                self.__reward_total += reward
                return True, reward, GameState(next_row, next_col, next_gem_status), is_game_over or is_solved

        elif action == self.JUMP:
            if self.grid_data[state.row + 1][state.col] == self.SUPER_JUMP_TILE:
                # sample a random move distance
                random.seed(seed)
                move_dist = self.__sample_move_dist(self.__super_jump_probs)

                next_row, next_col = state.row, state.col
                next_gem_status = state.gem_status

                # move sampled distance upwards
                for d in range(move_dist):
                    next_row -= 1
                    # check for collision or game over
                    next_row, next_col, reward, collision, is_game_over = \
                        self.__check_collision_or_terminal(next_row, next_col, reward, row_move_dir=-1, col_move_dir=0)
                    if collision or is_game_over:
                        break

                # check if a gem is collected or goal is reached (only do this for final position of charge)
                next_gem_status, is_solved = self.__check_gem_collected_or_goal_reached(next_row, next_col,
                                                                                        next_gem_status)

                self.__reward_total += reward
                return True, reward, GameState(next_row, next_col, next_gem_status), is_game_over or is_solved

            else:
                next_row, next_col = state.row - 1, state.col
                next_gem_status = state.gem_status
                # check for collision or game over
                next_row, next_col, reward, collision, is_game_over = \
                    self.__check_collision_or_terminal(next_row, next_col, reward, row_move_dir=-1, col_move_dir=0)
                # check if a gem is collected or goal is reached
                next_gem_status, is_solved = self.__check_gem_collected_or_goal_reached(next_row, next_col,
                                                                                        next_gem_status)

                self.__reward_total += reward
                return True, reward, GameState(next_row, next_col, next_gem_status), is_game_over or is_solved

        elif action in self.GLIDE_ACTIONS:
            # select probabilities to sample move distance
            if action in {self.GLIDE_LEFT_1, self.GLIDE_RIGHT_1}:
                probs = self.__glide1_probs
            elif action in {self.GLIDE_LEFT_2, self.GLIDE_RIGHT_2}:
                probs = self.__glide2_probs
            else:
                probs = self.__glide3_probs
            # sample a random move distance
            random.seed(seed)
            move_dist = self.__sample_move_dist(probs)

            # set movement direction
            if action in {self.GLIDE_LEFT_1, self.GLIDE_LEFT_2, self.GLIDE_LEFT_3}:
                move_dir = -1
            else:
                move_dir = 1

            # move sampled distance in chosen direction
            next_row, next_col = state.row + 1, state.col
            next_gem_status = state.gem_status

            # handle case where sampled glide distance is 0
            _, _, reward, _, is_game_over = self.__check_collision_or_terminal(next_row, next_col, reward,
                                                                               row_move_dir=0, col_move_dir=0)
            for d in range(move_dist):
                next_col += move_dir

                # check for collision or game over
                next_row, next_col, reward, collision, is_game_over = \
                    self.__check_collision_or_terminal_glide(next_row, next_col, reward,
                                                             row_move_dir=0, col_move_dir=move_dir)
                if collision or is_game_over:
                    break

            # check if a gem is collected or goal is reached (only do this for final position of charge)
            next_gem_status, is_solved = self.__check_gem_collected_or_goal_reached(next_row, next_col,
                                                                                    next_gem_status)

            self.__reward_total += reward
            return True, reward, GameState(next_row, next_col, next_gem_status), is_game_over or is_solved

        elif action in self.DROP_ACTIONS:
            move_dist = {self.DROP_1: 1, self.DROP_2: 2, self.DROP_3: 3}[action]

            # drop by chosen distance
            next_row, next_col = state.row, state.col
            next_gem_status = state.gem_status
            for d in range(move_dist):
                next_row += 1

                # check for collision or game over
                next_row, next_col, reward, collision, is_game_over = \
                    self.__check_collision_or_terminal_glide(next_row, next_col, reward, row_move_dir=1, col_move_dir=0)
                if collision or is_game_over:
                    break

            # check if a gem is collected or goal is reached (only do this for final position of charge)
            next_gem_status, is_solved = self.__check_gem_collected_or_goal_reached(next_row, next_col,
                                                                                    next_gem_status)

            self.__reward_total += reward
            return True, reward, GameState(next_row, next_col, next_gem_status), is_game_over or is_solved

        else:
            assert False, '!!! Invalid action given to perform_action() !!!'

    def is_solved(self, state):
        """
        Check if the game has been solved (i.e. player at exit and all gems collected)
        :param state: current GameState
        :return: True if solved, False otherwise
        """
        all_gems_collected = True
        for g in state.gem_status:
            if g == 0:
                all_gems_collected = False
        return state.row == self.exit_row and state.col == self.exit_col and all_gems_collected

    def is_game_over(self, state):
        """
        Check if a game over situation has occurred (i.e. player has entered on a lava tile)
        :param state: current GameState
        :return: True if game over, False otherwise
        """
        assert 0 < state.row < self.n_rows - 1 and 0 < state.col < self.n_cols - 1, '!!! invalid player coordinates !!!'
        return self.grid_data[state.row][state.col] == self.LAVA_TILE

    def render(self, state):
        """
        Render the map's current state to terminal
        """
        for r in range(self.n_rows):
            line = ''
            for c in range(self.n_cols):
                if state.row == r and state.col == c:
                    # current tile is player
                    line += self.grid_data[r][c] + 'P' + self.grid_data[r][c]
                elif self.exit_row == r and self.exit_col == c:
                    # current tile is exit
                    line += self.grid_data[r][c] + 'E' + self.grid_data[r][c]
                elif (r, c) in self.gem_positions and \
                        state.gem_status[self.gem_positions.index((r, c))] == 0:
                    # current tile is an uncollected gem
                    line += self.grid_data[r][c] + 'G' + self.grid_data[r][c]
                elif self.grid_data[r][c] in {self.SUPER_CHARGE_TILE, self.SUPER_JUMP_TILE}:
                    line += '[' + self.grid_data[r][c] + ']'
                else:
                    line += self.grid_data[r][c] * 3
            print(line)
        print('\n' * 2)

    def get_total_reward(self):
        """
        Get the total reward experienced so far (read only, writing this variable is not allowed)
        :return: total reward
        """
        return self.__reward_total
