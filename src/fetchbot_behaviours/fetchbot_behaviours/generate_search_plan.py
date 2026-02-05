import rclpy.node
import py_trees
from fetchbot_behaviours.types import NavGoal
from fetchbot_behaviours.location_info import LocationInfo
import random

from functools import partial



class GenerateSearchPlan(py_trees.behaviour.Behaviour):
    """Calls language service to parse command"""

    def __init__(self, name, node:rclpy.node.Node):
        super(GenerateSearchPlan, self).__init__(name)
        self.node = node
        self.blackboard = self.attach_blackboard_client()

        self.blackboard.register_key("target_object", access=py_trees.common.Access.READ)
        self.blackboard.register_key("nav_goal_queue", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("is_search_plan_generated", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("current_nav_goal", access=py_trees.common.Access.WRITE)
     
    def setup(self, **kwargs ):
        self.location_info = LocationInfo()
        pass
          
    def initialise(self):
        self.current_nav_goal:NavGoal = None
        self.goal_queue = None
        

        
    def update(self):

        if not self.blackboard.get("is_search_plan_generated"):
            self.generate_search_plan()
            if not self.blackboard.get("is_search_plan_generated"):
                return py_trees.common.Status.FAILURE
            else:
                return py_trees.common.Status.SUCCESS

        
        else:
            return py_trees.common.Status.SUCCESS
    
            

    
        

    def terminate(self, new_status):
        
        self.node.get_logger().warn(f"{self.name} {self.status} -> {new_status}")


    def generate_search_plan(self):
        self.target_object = None
        self.goal_queue = []

        self.target_object = self.blackboard.get("target_object")

        sorted_rooms = sorted(
            self.location_info.loc_probs[self.target_object].items(), # rooms sorted by probablities
            key=lambda item: item[1], 
            reverse=True
        )
        
        for room, prob in sorted_rooms:
            coords = self.location_info.search_locations[room].copy()
            # Shuffle coordinates within the room so search isn't identical every run
            random.shuffle(coords) 
            for x, y in coords:
                self.goal_queue.append(NavGoal(x, y, 0.0))

        self.blackboard.set("is_search_plan_generated", True)
        self.blackboard.set("nav_goal_queue", self.goal_queue)
        self.blackboard.set("current_nav_goal", self.goal_queue[0])


        self.node.get_logger().info(f"Generated search plan with {len(self.goal_queue)} points.")

        





        
 

