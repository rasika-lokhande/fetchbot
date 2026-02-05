import rclpy
from rclpy.node import Node
from fetchbot_interfaces.action import SearchObject
import py_trees
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from functools import partial
from rclpy.action.client import ClientGoalHandle, GoalStatus
from rclpy.task import Future

class Search(py_trees.behaviour.Behaviour):

    def __init__(self, name, node:Node):
        super(Search, self).__init__(name)
        self.node = node
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("target_object", access=py_trees.common.Access.READ)
        self.blackboard.register_key("object_found", access=py_trees.common.Access.WRITE)
        
      
    def setup(self, **kwargs ):
        self._action_client = ActionClient(
            self.node,
            SearchObject,
            'search_object')
        # Wait for action server
        self.node.get_logger().info("Waiting for search_object action server...")
        self._action_client.wait_for_server()
        self.node.get_logger().info("Action server available!")
       
    def initialise(self):
        self.target_object = None
        self.request_sent:bool = False
        self.is_goal_accepted = False
        self.goal_handle_ = None
        self.goal_future:Future = None
        self.result_future:Future = None
        self.result = None
        self.action_status = None
        pass

    def update(self):
        """
        Update method called by behavior tree on each tick.
        """
        # Step 1: Send search goal on first tick
        if not self.request_sent:
            self.target_object = self.blackboard.get("target_object")
            self.send_search_goal()
            self.request_sent = True
            self.node.get_logger().info("Sending search goal..")
            return py_trees.common.Status.RUNNING
        
        if self.request_sent and not self.is_goal_accepted:
            return py_trees.common.Status.FAILURE

        
        # Step 2: Waiting for goal acceptance
        if self.goal_future and not self.goal_future.done():
            return py_trees.common.Status.RUNNING
        
        # Step 3: Search in progress
        if not self.result_future or not self.result_future.done():
            return py_trees.common.Status.RUNNING

        # Step 4: Search results
        self.node.get_logger().info(f"Search here completed with result: {self.result}")
        if self.action_status == GoalStatus.STATUS_SUCCEEDED:
            if self.result.success == True:
                self.node.get_logger().info(f"Found Object!")
                self.blackboard.set("object_found", True)
                return py_trees.common.Status.SUCCESS
            else:
                self.node.get_logger().info(f"Did not find Object!")
                return py_trees.common.Status.FAILURE
        
        elif self.action_status == GoalStatus.STATUS_ABORTED:
            self.node.get_logger().error(f"Aborted")
            return py_trees.common.Status.FAILURE
        elif self.action_status == GoalStatus.STATUS_CANCELED: 
            self.node.get_logger().warn(f"Canceled")
            return py_trees.common.Status.FAILURE
        
        self.node.get_logger().info(f"Result: {str(self.result)}")

        
        

 
    def terminate(self, new_status):     
        self.request_sent = False
        self.is_goal_accepted = False
        self.goal_handle_ = None
        self.goal_future = None
        self.result_future = None
        self.result = None
        self.action_status = None
        self.node.get_logger().info(f"{self.name} {self.status} -> {new_status}")

    
    def send_search_goal(self):
        #create a goal
        goal = SearchObject.Goal()
        goal.target_object = self.target_object
        #send the goal
        self.goal_future = self._action_client.send_goal_async(goal)
        self.goal_future.add_done_callback(self.goal_response_callback)
    
   
    def goal_response_callback(self,future):
        # If goal is accepted, request the result
        self.goal_handle_:ClientGoalHandle = future.result()
        if self.goal_handle_.accepted:
            self.is_goal_accepted = True
            self.node.get_logger().info(f"Search Goal got accepted")
            self.result_future = self.goal_handle_.get_result_async()
            self.result_future.add_done_callback(self.goal_result_callback)
        else:
            self.node.get_logger().warn(f"Search Goal got rejected")
            self.is_goal_accepted = False


    def goal_result_callback(self,future):
        self.result = future.result().result
        self.action_status = future.result().status
       
        