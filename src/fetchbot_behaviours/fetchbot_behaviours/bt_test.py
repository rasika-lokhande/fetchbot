import py_trees
from py_trees.composites import Sequence, Selector
from fetchbot_behaviours.parse_command import ParseCommand
# Assuming you have or will create these:
# from fetchbot_behaviours.navigation import MoveTo, ScanObject, IsLocationKnown

def create_behavior_tree(node):
    """Construct the behavior tree structure"""

    # 1. Parse Command (Blackboard will store 'location' and 'object')
    # If object is unknown, this should return FAILURE to stop the tree.
    parse_cmd = ParseCommand("ParseCommand", node)

    # 2. Targeted Search (Sequence: Check if location exists -> Go to sub-locations)
    targeted_search = Sequence(name="Targeted Search", memory=True)
    # targeted_search.add_child(IsLocationKnown("Check Location")) 
    
    sub_loc_selector = Selector(name="Try Sub-Locations", memory=True)
    for i in range(1, 5):
        attempt = Sequence(name=f"Attempt Sub-{i}", memory=True)
        # attempt.add_child(MoveTo(f"sub_location_{i}"))
        # attempt.add_child(ScanObject()) # Returns SUCCESS if found, FAILURE if not
        sub_loc_selector.add_child(attempt)
    
    targeted_search.add_child(sub_loc_selector)

    # 3. Global Search (The Fallback)
    global_search = Sequence(name="Global Search", memory=True)
    # Add logic here to iterate over ALL locations if targeted search failed
    
    # 4. Strategy Selector
    # This will try Targeted Search first. If it fails (or location is unknown), 
    # it moves to Global Search.
    search_strategy = Selector(name="Search Strategy", memory=True)
    search_strategy.add_children([targeted_search, global_search])

    # Root Assembly
    root = Sequence(name="FetchAndDeliver", memory=True)
    root.add_children([parse_cmd, search_strategy])

    return py_trees.trees.BehaviourTree(root)