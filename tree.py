"""General Tree & Node Data Structures"""

from game_state import *
from game_env import *

# ---------------------------------------------------------------------------- #
#                                    CLASSES                                   #
# ---------------------------------------------------------------------------- #

class Node():
    def __init__(self, game_state, edge_cost, parent=None):
        self.parent = parent

        self.game_state = game_state

        self.edge_cost = edge_cost

        # Try to get an element from the gemstatus list - if no elems throw error
        try: game_state.gem_status[0]
        except:
            print("ERROR! Uh-Oh: This gem_state doesnt have spots for statuses for any gems. Are there no gems in this map? Maybe you should check that.")
            raise IndexError

        self.id = "#{}#{}#".format(game_state.row, game_state.col)
        for item in game_state.gem_status:
            print(item)
            self.id = self.id + str(item)
        print(self.id)

        self.children = []

    def __repr__(self):
        try: parent_id = self.parent.id
        except:
            parent_id = None

        return "[parent:{}, row:{}, col:{}, gem_status:{}, edge_cost:{}]".format(parent_id, self.game_state.row, self.game_state.col, self.game_state.gem_status, self.edge_cost)

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

        successor_states = {}

        # Pt1. ge the list of possible actions from this position
        actions = ['wl', 'wr', 'j'] # TODO: un-hardcode this

        # Pt2. Check if those actions are legal
        for action in actions:
            (legal, next_state) = game_env.perform_action(self.game_state, action)
            if legal:
                successor_states[action] = next_state
        
        # Pt3. convert successor states to successor nodes
        successor_nodes = []
        for (action, state) in successor_states.items():
            successor_nodes.append( Node(state, get_cost(action)) )

        """
        Perform the given action on the given state, and return whether the action was successful (i.e. valid and
        collision free) and the resulting new state.
        :param state: current GameState
        :param action: an element of self.ACTIONS
        :return: (successful [True/False], next_state [GameState])
        """


class Tree():
    def __init__(self, root_state):
        self.root = Node(root_state, 0)
        self.explored = []
        self.unexplored = []

    def show_all_nodes(self):
        all_nodes = self.explored + self.unexplored
        print(*all_nodes, sep = "\n")
        print('Tree Size:' + str(len(all_nodes)), '(Unexplored:' + str(len(self.unexplored)), ', Explored:' + str(len(self.explored))+")")


    def mark_explored(self, current_node):
        # Marks the current_node we have just explored as explored
        # print("Marking explored: {}".format(current_node))
        # Add the node to the explored list
        self.explored.append(current_node)
        # Remove the current_node from the unexplored list
        for node in self.unexplored:
            if node.id == current_node.id:
                # If we find a node with the same id in the unexplored list (we 
                # should always find exactly one), then remove it from the list
                self.unexplored.remove(node)

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

# ---------------------------------------------------------------------------- #
#                               TOP LVL FUNCTIONS                              #
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
#                                     MAIN                                     #
# ---------------------------------------------------------------------------- #

# Add a bunch of nodes
my_tree =  Tree(GameState(1, 1, ('0','0','0','0','0')))

current_node = my_tree.root
# Exploring the node to find new nodes...
my_tree.add_node(current_node, Node(GameState(1, 2, ('0','0','0','0','0')), 1.2))
my_tree.add_node(current_node, Node(GameState(2, 1, ('0','0','0','0','0')), 0.75))
my_tree.mark_explored(current_node)

current_node = current_node.children[0]
# Exploring the node to find new nodes...
my_tree.add_node(current_node, Node(GameState(1, 3, ('1','0','0','0','0')), 1.0))
my_tree.add_node(current_node, Node(GameState(2, 2, ('0','1','0','0','0')), 2.0))
my_tree.mark_explored(current_node)

# current_node = current_node.parent.children[1]

# # Now we are exploring a new position
# new_pos = (2,2)
# parent = current_node
# edge_cost = 

# # Check if there is a gem0 there (pretend we know is)
# gem0 = True
# if gem0:
#     gemstate = (current_node.gemstate or '0b10000')
# else:
#     gemstate = current_node.gemstate

# if False:
#     # If this point IS NOT previously explored in this gem state, then explore 
#     # it
#     pass
# else:
#     # If this point IS previously explored in this gem state, then check if the cost of this new path to this point has a ower cost than the previous path we took to it
    
#     # Get oldpathcost
#     # Get newpathcost
#     if newpathcost < oldpathcost:
#         # Prune the old path from the tree, and add the new path as a node to the tree
#         pass
#     else:
#         # This new path is not as good so do not add it as a node to the tree
#         pass
        


print("All Nodes:")
my_tree.show_all_nodes()
print("")


print("Explored:")
print(my_tree.explored)
print("")
print("Unexplored:")
print(my_tree.unexplored)
print("")