#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from fetchbot_interfaces.action import SearchObject
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
 
 
class ObjectSearchClientNode(Node): 
    def __init__(self):
        super().__init__("object_search_client") 

        self.declare_parameter('target_object', 'blue book')
        self.object_search_client = ActionClient(self, SearchObject, "search_object")
        self.target_object = self.get_parameter('target_object').value
        

    def send_search_goal(self):

        #wait for server
        self.object_search_client.wait_for_server()

        #create a goal
        goal = SearchObject.Goal()
        goal.target_object = self.target_object

        #send the goal
        self.object_search_client.send_goal_async(goal).add_done_callback(self.goal_response_callback)
        pass

    def goal_response_callback(self,future):
        # If goal is accepted, request the result
        self.goal_handle_:ClientGoalHandle = future.result()
        if self.goal_handle_.accepted:
            self.goal_handle_.get_result_async().add_done_callback(self.goal_result_callback)

    def goal_result_callback(self,future):
        result = future.result().result
        self.get_logger().info(f"Result: {str(result)}")
    
        pass

 
 
def main(args=None):
    rclpy.init(args=args)
    node = ObjectSearchClientNode() 
    node.send_search_goal()
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()