import rclpy.node
import py_trees
from fetchbot_behaviours.types import NavGoal
from fetchbot_behaviours.location_info import LocationInfo
import random

from functools import partial



class UpdateGoal(py_trees.behaviour.Behaviour):
    """Calls language service to parse command"""

    def __init__(self, name, node:rclpy.node.Node):
        super(UpdateGoal, self).__init__(name)
        self.node = node
        self.blackboard = self.attach_blackboard_client()
        

        self.blackboard.register_key("target_object", access=py_trees.common.Access.READ)
        self.blackboard.register_key("nav_goal_queue", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("current_nav_goal", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("is_search_plan_generated", access=py_trees.common.Access.WRITE)
        
        
        
     
    def setup(self, **kwargs ):
        pass
        
          
    def initialise(self):
        self.current_nav_goal:NavGoal = None
        self.goal_queue = None
        

        
    def update(self):

        if not self.blackboard.get("is_search_plan_generated"):
            self.generate_search_plan()
            

        self.goal_queue = self.blackboard.get("nav_goal_queue")
        # 1. If we have goals left in our queue
        if len(self.goal_queue) > 0:
            # Pop the first (best) goal
            self.current_nav_goal = self.goal_queue.pop(0)
            
            # 2. Update the blackboard for the Nav node
            self.blackboard.set("current_nav_goal", self.current_nav_goal)
            self.blackboard.set("nav_goal_queue", self.goal_queue)
            
            self.node.get_logger().info(f"Next nav goal: {self.current_nav_goal}")
            
            # 3. Return FAILURE to reset the Selector and trigger Child 1 (the Nav/Search sequence)
            return py_trees.common.Status.FAILURE
        
        # 2. If the queue is empty, we've exhausted all possibilities
        self.node.get_logger().warn("All search locations exhausted!")
        self.blackboard.set("is_search_plan_generated", False)
        return py_trees.common.Status.SUCCESS

        

    def terminate(self, new_status):
        
        self.node.get_logger().warn(f"{self.name} {self.status} -> {new_status}")


    def generate_search_plan(self):
        self.target_object = None
        self.goal_queue = []

        self.target_object = self.blackboard.get("target_object")

        sorted_rooms = sorted(
            LocationInfo.loc_probs[self.target_object].items(), # rooms sorted by probablities
            key=lambda item: item[1], 
            reverse=True
        )
        
        for room, prob in sorted_rooms:
            coords = LocationInfo.search_locations[room].copy()
            # Shuffle coordinates within the room so search isn't identical every run
            random.shuffle(coords) 
            for x, y in coords:
                self.goal_queue.append(NavGoal(x, y, 0.0))

        self.blackboard.set("is_search_plan_generated", True)
        self.blackboard.set("nav_goal_queue", self.goal_queue)

        self.node.get_logger().info(f"Generated search plan with {len(self.goal_queue)} points.")

        





        
 

