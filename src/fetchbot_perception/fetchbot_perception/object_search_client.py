#!/usr/bin/env python3

# A sample client node for search_object action server

import rclpy
from rclpy.node import Node
from fetchbot_interfaces.action import SearchObject
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle, GoalStatus
 
 
class ObjectSearchClientNode(Node): 
    def __init__(self):
        super().__init__("object_search_client") 

        self.declare_parameter('target_object', 'bottle')
        self.object_search_client = ActionClient(self, SearchObject, "search_object")
        self.target_object = self.get_parameter('target_object').value
        

    def send_search_goal(self):

        #wait for server
        self.object_search_client.wait_for_server()

        #create a goal
        goal = SearchObject.Goal()
        goal.target_object = self.target_object

        #send the goal
        self.object_search_client.send_goal_async(goal,self.feedback_callback).add_done_callback(self.goal_response_callback)
        
        #testing cancel goal
        #self.test_timer = self.create_timer(5.0, self.cancel_goal)


    def goal_response_callback(self,future):
        # If goal is accepted, request the result
        self.goal_handle_:ClientGoalHandle = future.result()
        if self.goal_handle_.accepted:
            self.get_logger().info(f"Goal got accepted")
            self.goal_handle_.get_result_async().add_done_callback(self.goal_result_callback)
        else:
            self.get_logger().warn(f"Goal got rejected")

    def goal_result_callback(self,future):
        result = future.result().result
        status = future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"Success!")
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error(f"Aborted")
        elif status == GoalStatus.STATUS_CANCELED: 
            self.get_logger().warn(f"Canceled")
        self.get_logger().info(f"Result: {str(result)}")
    
    def feedback_callback(self, feedback_msg):
        elapsed_time = feedback_msg.feedback.elapsed_time
        current_vel = feedback_msg.feedback.current_velocity
        self.get_logger().info(f"Current cmd vel rot: {current_vel.twist.angular.z}")
        pass

    def cancel_goal(self):
        self.get_logger().warn("Sending cancel request")
        self.goal_handle_.cancel_goal_async()
        #self.test_timer.cancel() #for testing

 
 
def main(args=None):
    rclpy.init(args=args)
    node = ObjectSearchClientNode() 
    node.send_search_goal()
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()