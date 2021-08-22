from game_env import GameEnv
from game_state import GameState
import time

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

    def __repr__(self):
        try: parent_id = self.parent.id
        except:
            parent_id = None

        return "<id:{},parent_id:{},row:{},col:{},gem_status:{},edge_action:{}>".format(self.id, parent_id, self.game_state.row, self.game_state.col, self.game_state.gem_status, self.edge_action)

    def get_successors(self, game_env):
        # TODO: Test this function
        # Gets the possible successor nodes from this node.
        # Tries each possible move from current position. For each of the 
        # possible moves, check if the move is legal, and if it is, get the 
        # resultant node for that move and add is to the successors list
        # 
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

    def get_matching_node(self, current_node):
        """ 
        Checks whether the tree already contains a node with the same gamestate, and returns it if there is.

        Returns:
            the matching node -  if there is a node with same game_state
            False -  if there are no matches
        """
        all_nodes = self.explored + self.unexplored
        for node in all_nodes:
            if current_node.game_state == node.game_state:
                # This node has the same game_state as our current node, so return True
                return node
        # If we get to here without returning True, then we have gone through the whole list of nodes without finding any with a matching game_state, so return False
        return None

    def explore(self, game_env):
        # Get the next node to explore
        try: current_node = self.unexplored.pop(0)
        except IndexError:
            # If we get here, then the tree has explored all possible nodes and found no solution, so raise an error?
            print("REACHED END OF UNEXPLORED LIST WITHOUT SOLUTION")
            print("UH-OH SEARCH PROBLEM IS UNSOLVABLE :(, Raising RuntimeError...")
            raise RuntimeError
            
        # Move that node to the explored list
        self.explored.append(current_node)
        # Get all of the new nodes that expand out from the current node
        successors = current_node.get_successors(game_env)

        # Check if successors contains any states we have visited before
        for successor in successors:
            # Check if this successor solves the search problem (all gems + exit)
            if game_env.is_solved(successor.game_state):
                # Add it to the unexplored list (since it is a fringe node)
                self.unexplored.append(successor)
                # Return this solution node
                return successor

            # If we have visited this state before, check if this current path is less costly than the previous lowest cost path to this state
            previous_visit = self.get_matching_node(successor)
            if not previous_visit:
                # If we either haven't visited this node before, add it to the unexplored list
                self.unexplored.append(successor)

            elif self.get_path_cost(successor) < self.get_path_cost(previous_visit):
                # Also if we have visited before but this new path is less costly than the last path, add it to the unexplored list, and also remove the previous_visit from the explored nodes list
                
                # print(previous_visit)
                # print(successor)
                # print("")
                # print("EXPLORED:")
                # print(self.explored)
                # print("")  . 
                # print("UNEXPLORED:")
                # print(self.unexplored)

                # Append the new visit
                self.unexplored.append(successor)
                # Remove the old visit
                try: 
                    self.explored.remove(previous_visit)
                except ValueError:
                    self.unexplored.remove(previous_visit)

            else:
                # Else, prune this node from the sucessor list - it will not be added to the tree for further exploration
                pass
        return None

    def get_path(self, node):
        """
        Gets the full path to node from the initial starting point
        
        Works by recursively finding the path of the parent
        
        """
        # Check to see if i have no parent (i.e. im the root node) (base case) 
        if node.parent == None:
            # print("I have no parent")
            return []
        else:
            # print("My edge action: {}. Looking up parent ...".format(node.edge_action))
            path = self.get_path(node.parent) + [node.edge_action]
            return path

    def get_path_cost(self, node):
        """
        Gets the cost of the full path to node from the initial starting point
        
        Works by using the code we already wrote for get_path
        
        """
        path = self.get_path(node)
        total_cost = 0
        for action in path:
            total_cost = total_cost + ACTION_COST[action]
        return total_cost

# ---------------------------------------------------------------------------- #
#                               HELPER FUNCTIONS                               #
# ---------------------------------------------------------------------------- #


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
    print("########################")
    # Do stuff
    print("Running ucs algorithm...")
    start_time = time.time()

    # Read the input testcase file
    initial_state = game_env.get_init_state()
    # Init the tree data structure
    my_tree =  Tree(initial_state)

    # Pop the first element from the unexplored queue and explore it
    i=0
    running = True
    while running:
        # print("_________Step {}_________".format(i))
        solution = my_tree.explore(game_env)
        if solution == None:
            i = i+1
        else:
            running = False
        
    # If we get here than we have successfully found a solution to the problem (not necessarily optimal)
    # print("YAY, A SOLUTION IS FOUND!")

    # print("Explored:")
    # print(my_tree.explored)
    # print("")
    # print("Unexplored:")
    # print(my_tree.unexplored)
    # print("")


    print("Solution:")
    print(solution)
    # Get the path (actions list) to the solution node and return it
    print("ACTIONS: {}".format(my_tree.get_path(solution)))
    print("COST: {}".format(my_tree.get_path_cost(solution)))

    print("Time to execute: {} second(s)".format(round((time.time()-start_time), 4)))

    print("########################")
    # Return the final list of actions
    return my_tree.get_path(solution)

if __name__ == '__main__':
    # Do stuff
    pass

