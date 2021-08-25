from game_env import GameEnv
from game_state import GameState
import time

import heapq

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
#                         CONSTANTS & GLOBAL VARIABLES                         #
# ---------------------------------------------------------------------------- #

# input file symbols
SOLID_TILE = 'X'
LADDER_TILE = '='
AIR_TILE = ' '
LAVA_TILE = '*'
GEM_TILE = 'G'
EXIT_TILE = 'E'
PLAYER_TILE = 'P'
VALID_TILES = {SOLID_TILE, LADDER_TILE, AIR_TILE, LAVA_TILE, GEM_TILE, EXIT_TILE, PLAYER_TILE}

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
ACTION_COST = {WALK_LEFT: 1.0, WALK_RIGHT: 1.0, JUMP: 2.0, GLIDE_LEFT_1: 0.7, GLIDE_LEFT_2: 1.0, GLIDE_LEFT_3: 1.2,
                GLIDE_RIGHT_1: 0.7, GLIDE_RIGHT_2: 1.0, GLIDE_RIGHT_3: 1.2, DROP_1: 0.3, DROP_2: 0.4, DROP_3: 0.5}
POSSIBLE_ACTIONS = {SOLID_TILE : [WALK_LEFT,WALK_RIGHT,JUMP], 
                    LADDER_TILE : [WALK_LEFT,WALK_RIGHT,JUMP,GLIDE_LEFT_1,GLIDE_LEFT_2,GLIDE_LEFT_3,GLIDE_RIGHT_1,GLIDE_RIGHT_2,GLIDE_RIGHT_3,DROP_1,DROP_2,DROP_3], 
                    AIR_TILE : [GLIDE_LEFT_1,GLIDE_LEFT_2,GLIDE_LEFT_3,GLIDE_RIGHT_1,GLIDE_RIGHT_2,GLIDE_RIGHT_3,DROP_1,DROP_2,DROP_3], 
                    LAVA_TILE : [], # standing above a lava tile results in a gameover
                    AIR_TILE : [GLIDE_LEFT_1,GLIDE_LEFT_2,GLIDE_LEFT_3,GLIDE_RIGHT_1,GLIDE_RIGHT_2,GLIDE_RIGHT_3,DROP_1,DROP_2,DROP_3], 
                    AIR_TILE : [GLIDE_LEFT_1,GLIDE_LEFT_2,GLIDE_LEFT_3,GLIDE_RIGHT_1,GLIDE_RIGHT_2,GLIDE_RIGHT_3,DROP_1,DROP_2,DROP_3], 
                    }

# badcounter = 0

# ---------------------------------------------------------------------------- #
#                                    CLASSES                                   #
# ---------------------------------------------------------------------------- #
class Node():
    def __init__(self, game_state, actions, path_cost, parent=None):
        # self.parent = parent
        self.game_state = game_state
        self.actions = actions # the action we took to get to this node
        self.path_cost = path_cost # the cost of the full path to this node from the initial node

    def __repr__(self):
        return "<row:{},col:{},gem_status:{},actions:{},path_cost:{}>".format(self.game_state.row, self.game_state.col, self.game_state.gem_status, self.actions, self.path_cost)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.game_state == other.game_state# and self.path_cost == other.path_cost

    def __hash__(self):
        # return hash(self.game_state)
        return hash((self.game_state.row, self.game_state.col, self.game_state.gem_status))

    def __lt__(self, other):
        return True
        # return self.path_cost < other.path_cost

    def get_successors(self, game_env):
        # Gets the possible successor nodes from this node.
        # Tries each possible move from current position. For each of the 
        # possible moves, check if the move is legal, and if it is, get the 
        # resultant node for that move and add is to the successors list
        # 
        # Returns:
        #     successors: a list of nodes it is possible to visit from the 
        #         current node
        successor_nodes = []

        # # Get the possible actions for the tile type we are standing on
        actions = POSSIBLE_ACTIONS[game_env.grid_data[self.game_state.row + 1][self.game_state.col]]

        for action in actions:
            # TODO: Can we make this any more efficient?
            (legal, next_state) = game_env.perform_action(self.game_state, action) # Test whether this move is legal or not
            if legal:
                # Convert successor states to successor nodes
                successor_nodes.append( Node(next_state, self.actions+[action], self.path_cost+ACTION_COST[action], parent=self) )
        return successor_nodes
        

# ---------------------------------------------------------------------------- #
#                               HELPER FUNCTIONS                               #
# ---------------------------------------------------------------------------- #

def show_num_nodes(unexplored, explored):
    num_explored = len(explored)
    num_unexplored = len(unexplored)
    print('[[ Tree Size:' + str(num_explored+num_unexplored), '(Unexplored:' + str(num_unexplored), ', Explored:' + str(num_explored)+") ]]")

# def get_path(node):
#     """
#     Gets the full path to node from the initial starting point
    
#     Works by recursively finding the path of the parent
    
#     """
#     # Check to see if i have no parent (i.e. im the root node) (base case) 
#     if node.parent == None:
#         return []
#     else:
#         path = get_path(node.parent) + [node.actions]
#         return path

def get_matching_node(unexplored, current_node):
    """ 
    Checks whether the tree already contains a node with the same gamestate, and returns it if there is.

    Returns:
        the matching node -  if there is a node with same game_state
        None -  if there are no matches
    """

    for unexplored_node in unexplored:
        if current_node.game_state == unexplored_node.game_state:
            return unexplored_node   
    return None

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
    print("[[ Running ucs algorithm... ]]")
    start_time = time.time()

    # Read the input testcase file
    initial_state = game_env.get_init_state()

    # Create a set to hold the nodes that have been explored from
    explored = {initial_state: 0}
    # Create a PriorityQueue to hold the nodes that have been explored from
    unexplored = [(0, Node(initial_state,[],0))]
    heapq.heapify(unexplored)

    while len(unexplored) > 0:
        # Get the next node to explore
        _, current_node = heapq.heappop(unexplored)

        # Check if this node solves the search problem
        if game_env.is_solved(current_node.game_state):
            # Yay, we found a solution!!!
            show_num_nodes(unexplored, explored)
            print("[[ My Execution Time: {} Second(s) ]]".format(round((time.time()-start_time), 4)))
            return current_node.actions

        # Get all of the new nodes that expand out from the current node
        successors = current_node.get_successors(game_env)
        for successor in successors:
            # If the state is previously explored, can this node immediately
            if successor.game_state not in explored.keys() or successor.path_cost < explored[successor.game_state]:
                # Add to lists
                explored[successor.game_state] = successor.path_cost
                heapq.heappush(unexplored, (successor.path_cost, successor))

    return None

if __name__ == '__main__':
    # Do stuff
    pass

