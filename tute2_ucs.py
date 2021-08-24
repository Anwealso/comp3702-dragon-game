# # Tutorial 2

# Let us recall the components we need for an agent.
# - Action Space (A)
# - Percept Space (P) 
# - State Space (S)
# - Transition Function (T : S x A -> S')
# - Utility Function (U: S -> R)
# 
# We know the problem is fully observable, thus the percept space is the same as the state space and we dont need to do anything special while considering it. For BFS and DFS problems there is no cost associated with actions, the utility will therefore become 1 for reaching the goal state and 0 otherwise.
# 
# That leaves us with action space, state space, and transition function.
# 
# In the 8-puzzle game there are 4 actions that are available to us, Up, Right, Down, Left. These 4 actions make up the action space, the actions are not all always available, however we will worry about that when getting to the transition function.
# 
# The transition function is the core of the problem, given a state and an action we need a way to find the next state. The implementation for this will largely depend on the state space, so let's start with that. 
#   

# ## State Representation
# 
# Let's start by defining the state space in terms of Python code. There are a few things we will be interested in. 
# - The grid layout: What numbers are in what positions? We will treat this as a list, however there are a number of ways we can model it
# - What action led to here?
# - What was the previous state?
# - Whether the cell visited or not
# 
# To keep track of all these properties, let's start by defining a class.
# 
# We'll also keep track of the cost. This is not needed for BFS and DFS, however is very important when we get to UCS.

# We'll need this later for Uniform Cost Search
from queue import *
import heapq

# We'll need this to copy states
import copy

# State representation
class Node:
    def __init__(self, grid, previous_action, parent):
        self.grid = grid
        self.previous_action = previous_action
        self.parent = parent
        self.total_cost = 0 # For UCS

    @staticmethod
    def to_1d(x, y):
        return (3 * y) + x

    @staticmethod
    def to_2d(i):
        return i % 3, i // 3
    
    @staticmethod
    def is_valid_pos_2d(x, y):
        return 0 <= x and x < 3 and 0 <= y and y < 3
    
    # Override equality and hash - needed to check when 2 states are equal
    # It would otherwise default to checking object references
    def __eq__(self, other):
        return self.grid == other.grid
    
    def __hash__(self):
        return hash(tuple(self.grid))
    
    def print(self, description):
        print(description);
        for y in range(3):
            for x in range(3):
                print("{:^3}".format(str(self.grid[self.to_1d(x, y)])), end='')
            print()
        print()

    def get_blank_i(self):
        return self.grid.index("_")

    @staticmethod
    def get_blank_tile_neighbours(x, y):
        """
        Takes blank tile coordinates and for every action in A returns where it would go.
        """
        return {'L': (x - 1, y),
                'R': (x + 1, y),
                'U': (x, y - 1),
                'D': (x, y + 1)}

    def get_children(self):
        # Current blank tile location
        i_old = self.get_blank_i()
        x_old, y_old = self.to_2d(i_old)
        
        # Neighbouring blank tile locations
        neighbours = self.get_blank_tile_neighbours(x_old, y_old)
        
        # For valid neighbouring positions, swap the tiles around
        children = list()
        for a, n in neighbours.items():
            x_new, y_new = n[0], n[1]
            if self.is_valid_pos_2d(x_new, y_new):
                succ_state = copy.deepcopy(self.grid) # We don't want to ruin the previous state's grid
                i_new = self.to_1d(x_new, y_new)
                succ_state[i_old], succ_state[i_new] = succ_state[i_new], succ_state[i_old]
                succ = Node(succ_state, a, self)
                children.append(succ)
                
        return children

# ## Uniform Cost Search
# 
# The last part is to convert our BFS code to UCS. The difference here is that UCS keeps track of the cost of actions. We are given that the cost of actions is {Up=1, Down=2, Left=3, Right=4}. In other words, going up 4 times is as expensive as going right once. We are no longer concerned with minimising the number of moves, instead we want to minimize the cost.
# 
# Let's add this to our representation of the game:

class Node(Node): # Continued
    # Returns cost of making an action
    def get_cost(self):
        if(self.previous_action == 'U'):
            return 1
        elif(self.previous_action == 'D'):
            return 2
        elif(self.previous_action == 'L'):
            return 3
        elif(self.previous_action == 'R'):
            return 4
        else:
            raise Exception("Invalid action: {}".format(self.action))
    
    # Override less than function for UCS
    def __lt__(self, other):
        return self.total_cost < other.total_cost


# In our Node class above we keep track of the aggregate cost from the start position to each new state. To make use of this we will use a priority queue (`heapq`), which takes elements out that have the smallest cost.
# 
# You'll notice we also made function `__lt__`, this is an override for the less than operator (<), which we will use for UCS to compare the total cost of two states.

# Uniform Cost Search
def uniform_cost_search(init_state, goal_state):
    print("Running Uniform Cost Search...")
    visited = set()

    pq = []
    pq.append(init_state)
    heapq.heapify(pq)

    while pq:
        node = heapq.heappop(pq)
        if node == goal_state:
            print ("We reached the goal, Jolly Good!")
            break;
        if node not in visited:
            visited.add(node)

        children = node.get_children()
        for succ in children:
            if succ not in visited:
                # Calculate total cost and add to unexplored nodes
                succ.total_cost = node.total_cost + succ.get_cost()
                heapq.heappush(pq, succ)

    if not pq:
        node = None
        
    return node, visited
        
goal_node, visited = uniform_cost_search(init_state, goal_state)
backtrack_actions(goal_node, visited)


# Notice that very little changed from the previous code, we replaced the queue with the heapq. The heapq will always take the item with the lowest value from the queue. Since we overrode the less than `__lt__` operator in our class, the `heapq` knows how to compare the elements.