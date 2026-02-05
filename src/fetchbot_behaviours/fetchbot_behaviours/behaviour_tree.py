import py_trees
from py_trees.composites import Sequence, Selector
from fetchbot_behaviours.parse_command import ParseCommand
from fetchbot_behaviours.nav_location import NavLocation
from fetchbot_behaviours.search import Search
from fetchbot_behaviours.update_goal import UpdateGoal
from fetchbot_behaviours.generate_search_plan import GenerateSearchPlan


# nav_goal = NavGoal(6.0,2.0,0.0)
# target_object = 'green bottle'

def create_behavior_tree(node):
    """Construct the behavior tree structure"""
    blackboard = py_trees.blackboard.Client()


    
    
    
    parse_command = ParseCommand("Parse Command", node)
    generate_search_plan = GenerateSearchPlan("Generate Search Plan", node)


    search_attempt = Sequence(name=f"Searching",
            memory=True,
            children=[
            NavLocation("Nav2Location", node), 
            Search("Search", node)])
    
    update_goal = UpdateGoal("Update goal", node)
   
    
    
    search_strategy = Selector(name="Search Strategy", memory=False,
                               children=[
                                   search_attempt,
                                   update_goal
                               ])

    

    root = Sequence(
        name="Look for object",
        memory=True,  
        children=[
          parse_command,
          generate_search_plan,
          search_strategy 
          ]) # Write child behaviours in order
    
    
    return py_trees.trees.BehaviourTree(root)