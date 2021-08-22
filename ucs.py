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
#                                    CLASSES                                   #
# ---------------------------------------------------------------------------- #
class Node():
    def __init__(self, game_state, edge_action, parent=None):
        self.parent = parent

        self.game_state = game_state

        self.edge_action = edge_action # the action we took to get to this node

        # self.edge_cost = edge_cost # TODO: remove edge_cost (since is recoverable from edge_action)

        # Try to get an element from the gemstatus list - if no elems throw error
        try: game_state.gem_status[0]
        except:
            print("ERROR! Uh-Oh: This gem_state doesnt have spots for statuses for any gems. Are there no gems in this map? Maybe you should check that.")
            raise IndexError

        self.id = "#{}#{}#".format(game_state.row, game_state.col)
        for item in game_state.gem_status:
            self.id = self.id + str(item)

        self.children = []

    def __repr__(self):
        try: parent_id = self.parent.id
        except:
            parent_id = None

        return "[id:{},parent_id:{},row:{},col:{},gem_status:{},edge_action:{}]".format(self.id, parent_id, self.game_state.row, self.game_state.col, self.game_state.gem_status, self.edge_action)

    def get_child_nodes(self,nodes_list):
        for child in self.children:
            if child.children:
                # If our child has children
                nodes_list.append(child)
                child.get_child_nodes(nodes_list)
            else:
                nodes_list.append(child)

    def get_successors(self, game_env):
        # TODO: Test this function
        # Gets the possible successor nodes from this node.
        # Tries each possible move from current position. For each of the 
        # possible moves, check if the move is legal, and if it is, get the 
        # resultant node for that move and add is to the successors list
        # Returns:
        #     successors: a list of nodes it is possible to visit from the 
        #         current node

        # Pt1. ge the list of possible actions from this position
        actions = ['wl', 'wr', 'j', 'gl1', 'gl2', 'gl3', 'gr1', 'gr2', 'gr3', 'd1', 'd2', 'd3']

        # Pt2. Check if those actions are legal
        successor_states = {}
        for action in actions:
            (legal, next_state) = game_env.perform_action(self.game_state, action)
            if legal:
                successor_states[action] = next_state
        
        # Pt3. convert successor states to successor nodes
        successor_nodes = []
        for (action, state) in successor_states.items():
            successor_nodes.append( Node(state, action, parent=self) )

        return successor_nodes
        

class Tree():
    def __init__(self, root_state):
        self.root = Node(root_state, '')
        self.explored = []
        self.unexplored = [] # <-- this needs to be a queue (pop from front, add to back)
        self.unexplored.append(self.root)

    def show_all_nodes(self):
        all_nodes = self.explored + self.unexplored
        print(*all_nodes, sep = "\n")
        print('Tree Size:' + str(len(all_nodes)), '(Unexplored:' + str(len(self.unexplored)), ', Explored:' + str(len(self.explored))+")")

    def show_num_nodes(self):
        all_nodes = self.explored + self.unexplored
        print('Tree Size:' + str(len(all_nodes)), '(Unexplored:' + str(len(self.unexplored)), ', Explored:' + str(len(self.explored))+")")

    # def mark_explored(self, current_node):
    #     # Marks the current_node we have just explored as explored
    #     # print("Marking explored: {}".format(current_node))
    #     # Add the node to the explored list
    #     self.explored.append(current_node)
    #     # Remove the current_node from the unexplored list
    #     for node in self.unexplored:
    #         if node.id == current_node.id:
    #             # If we find a node with the same id in the unexplored list (we 
    #             # should always find exactly one), then remove it from the list
    #             self.unexplored.remove(node)

    def add_node(self, parent, node):
        # Adds an unexplored node to the tree given a node object and a parent node object
        node.parent = parent
        parent.children.append(node)
        self.unexplored.append(node)

    def add_nodes(self, parent, nodes):
        # Adds a number of nodes all with the same parent
        for node in nodes:
            node.parent = parent
            parent.children.append(node)
            self.unexplored.append(node)

    def explore(self, game_env):
        # Get the next node to explore
        current_node = self.unexplored.pop(0)
        # Move that node to the explored list
        self.explored.append(current_node)
        # Add the new nodes found to the unexplored list
        self.unexplored = self.unexplored + current_node.get_successors(game_env)

    def get_path(self, node):
        """
        Gets the full path to node from the initial starting point
        
        Works by recursively finding the path of the parent
        
        """
        # print(1)

        # Check to see if i have no parent (i.e. im the root node) (base case) 
        if node.parent == None:
            # print("I have no parent")
            return []
        else:
            # print("My edge action: {}. Looking up parent ...".format(node.edge_action))
            path = self.get_path(node.parent) + [node.edge_action]
            return path

# ---------------------------------------------------------------------------- #
#                               HELPER FUNCTIONS                               #
# ---------------------------------------------------------------------------- #
def get_cost(move):
    # Gets the possible successor nodes from this node.
    # Tries each possible move from current position. For each of the 
    # possible moves, check if the move is legal, and if it is, get the 
    # resultant node for that move and add is to the successors list
    # Args:
    #     move: a string representing a move, e.g. 'wr', 'j'
    # Returns:
    #     cost: the cost of the given move (as a float)

    cost_dict = {'wl':1.0, 'wr':1.0, 'j':2.0, 
        'gl1':0.7, 'gl2':1.0, 'gl3':1.2, 'gr1':0.7, 'gr2':1.0, 'gr3':1.2, 
        'd1':0.3, 'd2':0.4, 'd3':0.5}
    cost = cost_dict[move]

    return cost


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
    print("##########################################")

    # Do stuff
    print("Running ucs algorithm...")

    # Read the input testcase file
    initial_state = game_env.get_init_state()
    # Init the tree data structure
    my_tree =  Tree(initial_state)

    # Pop the first element from the unexplored queue and explore it
    for i in range(200):
        my_tree.explore(game_env)
        print("_________Step {}_________".format(i))

    print("Explored:")
    print(my_tree.explored)
    print("")
    print("Unexplored:")
    print(my_tree.unexplored)
    print("")

    my_tree.show_num_nodes()
    print("")

    # Get the path to the last node we explored and return that
    # TODO: update this later to returning the fully slved path
    actions = my_tree.get_path(my_tree.explored[-1])
    print("ACTIONS: {}".format(actions))

    print("##########################################")
    # Return the final list of actions
    return actions

if __name__ == '__main__':
    # Do stuff
    pass

