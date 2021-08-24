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

ACTION_COST = {'wl':1.0, 'wr':1.0, 'j':2.0, 
        'gl1':0.7, 'gl2':1.0, 'gl3':1.2, 'gr1':0.7, 'gr2':1.0, 'gr3':1.2, 
        'd1':0.3, 'd2':0.4, 'd3':0.5}

# ---------------------------------------------------------------------------- #
#                                    CLASSES                                   #
# ---------------------------------------------------------------------------- #
class Node():
    def __init__(self, game_state, edge_action, path_cost, parent=None):
        self.parent = parent
        self.game_state = game_state
        self.edge_action = edge_action # the action we took to get to this node
        self.path_cost = path_cost # the cost of the full path to this node from the initial node

    def __repr__(self):
        return "<row:{},col:{},gem_status:{},edge_action:{},path_cost:{}>".format(self.game_state.row, self.game_state.col, self.game_state.gem_status, self.edge_action, self.path_cost)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.game_state == other.game_state# and self.path_cost == other.path_cost

    def __hash__(self):
        # TODO: Check if putting self.parent in the hash function is bad/slow
        return hash(self.game_state)

    def __lt__(self, other):
        return self.path_cost < other.path_cost

    def get_successors(self, game_env):
        # TODO: Maybe look at optimising this function???
        # Gets the possible successor nodes from this node.
        # Tries each possible move from current position. For each of the 
        # possible moves, check if the move is legal, and if it is, get the 
        # resultant node for that move and add is to the successors list
        # 
        # Returns:
        #     successors: a list of nodes it is possible to visit from the 
        #         current node

        # Pt1. get the list of possible actions from this position
        actions = ['wl', 'wr', 'j', 'gl1', 'gl2', 'gl3', 'gr1', 'gr2', 'gr3', 'd1', 'd2', 'd3']

        # Pt2. Check if those actions are legal
        successor_states = {}
        for action in actions:
            # TODO: Maybe we can find a more efficient way of testing whether this move is legal or not?
            (legal, next_state) = game_env.perform_action(self.game_state, action)
            if legal:
                successor_states[action] = next_state
        
        # Pt3. convert successor states to successor nodes
        successor_nodes = []
        for (action, state) in successor_states.items():
            successor_nodes.append( Node(state, action, self.path_cost+ACTION_COST[action], parent=self) )

        return successor_nodes
        

# ---------------------------------------------------------------------------- #
#                               HELPER FUNCTIONS                               #
# ---------------------------------------------------------------------------- #

def show_num_nodes(unexplored, explored):
    num_explored = len(explored)
    num_unexplored = len(unexplored)
    print('[[ Tree Size:' + str(num_explored+num_unexplored), '(Unexplored:' + str(num_unexplored), ', Explored:' + str(num_explored)+") ]]")

def get_path(node):
    """
    Gets the full path to node from the initial starting point
    
    Works by recursively finding the path of the parent
    
    """
    # Check to see if i have no parent (i.e. im the root node) (base case) 
    if node.parent == None:
        return []
    else:
        path = get_path(node.parent) + [node.edge_action]
        return path

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

# TODO: Look at maybe whether the encapsulation of this tree object is making things run much slower    


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
    explored = set()
    # Create a PriorityQueue to hold the nodes that have been explored from
    unexplored = []
    unexplored.append(Node(initial_state, '', 0))
    heapq.heapify(unexplored)

    solution = None

    while not solution:
        # Get the next node to explore
        current_node = heapq.heappop(unexplored)
        # Move that node to the explored list
        explored.add(current_node)

        # Get all of the new nodes that expand out from the current node
        successors = current_node.get_successors(game_env)
        for successor in successors:
            # Check if this node solves the search problem
            if game_env.is_solved(successor.game_state):
                # Yay, we found a solution!!!
                solution = successor
                break

            # If the state is previously explored, can this node immediately
            if successor not in explored:
                # If the state is NOT previously explored, only add this new path if it has a lower cost than the existing path
                previous_unexplored = get_matching_node(unexplored, successor)
                if not previous_unexplored:
                    # Add it to the unexplored list (since it is a fringe node)
                    heapq.heappush(unexplored, successor)
                elif successor.path_cost < previous_unexplored.path_cost:
                    # Add this new path to the unexplored list (since it is a fringe node)
                    heapq.heappush(unexplored, successor)
                    # Remove the previous_visit from the unexplored list
                    unexplored.remove(previous_unexplored)

    if not solution:
        # If this error raises, then it means no solution was found
        raise RuntimeError

    # If we found a solution, get its path
    solution_path = get_path(solution)

    show_num_nodes(unexplored, explored)
    print("[[ Execution Time: {} Second(s) ]]".format(round((time.time()-start_time), 4)))

    # Return the final list of actions
    return solution_path

if __name__ == '__main__':
    # Do stuff
    pass

