import py_trees
from py_trees.composites import Sequence, Selector
from fetchbot_behaviours.parse_command import ParseCommand
from fetchbot_behaviours.nav_location import NavLocation
from fetchbot_behaviours.search import Search
from fetchbot_behaviours.types import NavGoal


nav_goal = NavGoal(6.0,2.0,0.0)
target_object = 'green bottle'

def create_behavior_tree(node):
    """Construct the behavior tree structure"""

    root = Sequence(
        name="Look for object",
        memory=True,  
        children=[
          # ParseCommand("ParseCommand", node),
          NavLocation("Nav2Location", node, nav_goal),
          Search("Search", node, target_object=target_object) ]) # Write child behaviours in order
    
    
    return py_trees.trees.BehaviourTree(root)