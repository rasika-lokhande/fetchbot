import py_trees
from py_trees.composites import Sequence, Selector
from fetchbot_behaviours.parse_command import ParseCommand
from fetchbot_behaviours.nav_location import NavLocation
from fetchbot_behaviours.types import NavGoal


nav_goal = NavGoal(6.0,2.0,0.0)

def create_behavior_tree(node):
    """Construct the behavior tree structure"""

    root = Sequence(
        name="FetchAndDeliver",
        memory=True,  
        children=[
           ParseCommand("ParseCommand", node),
            NavLocation("Nav2Location", node, nav_goal)]) # Write child behaviours in order
    
    
    return py_trees.trees.BehaviourTree(root)