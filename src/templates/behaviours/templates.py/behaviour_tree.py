# behavior_tree_node.py
import py_trees
from py_trees.composites import Sequence, Selector
from .behaviors import *
from .blackboard_keys import BlackboardKeys

def create_behavior_tree(node):
    """Construct the behavior tree structure"""
    
    # Main task sequence
    root = Sequence(
        name="FetchAndDeliver",
        memory=False,  # Don't remember child states
        children=[
            ParseCommand("ParseCommand", node),
            
            NavigateToLocation("NavToSource", node, BlackboardKeys.SOURCE_LOCATION),
            
            # Search with fallback recovery
            Selector(
                name="SearchWithRecovery",
                children=[
                    SearchForObject("SearchObject", node),
                    # If search fails, could add recovery behaviors here
                    py_trees.behaviours.Failure("ObjectNotFound")
                ]
            ),
            
            # Approach object (simplified - just assume we're close enough)
            
            SimulateGrasp("Grasp", node),
            
            NavigateToLocation("NavToDest", node, BlackboardKeys.DEST_LOCATION),
            
            SimulateGrasp("Release", node),  # Reuse grasp behavior for release
        ]
    )
    
    return py_trees.trees.BehaviourTree(root)