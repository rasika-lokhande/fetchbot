#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup



from geometry_msgs.msg import TwistStamped
from fetchbot_interfaces.msg import ClipDetection
from fetchbot_interfaces.action import SearchObject


class ObjectSearchNode(Node):
    """
    ROS2 Action server that rotates the robot to search for an object.

    Subscribes to: /detected_objects
    Publishes to: /cmd_vel
    Action: /search_object
    """

    def __init__(self):
        super().__init__('object_search')

        self.declare_parameter('rotation_speed', 0.5)          # rad/s
        self.declare_parameter('confidence_threshold', 0.99)
        self.declare_parameter('max_search_time', 30.0)        # seconds
        self.declare_parameter('search_freq', 10.0)            # Hz

        self.rotation_speed = self.get_parameter('rotation_speed').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.max_search_time = self.get_parameter('max_search_time').value
        self.search_freq = self.get_parameter('search_freq').value
        self.latest_detection = None

        self.detection_sub = self.create_subscription(
            msg_type=ClipDetection,
            topic='/detection_result',
            callback = self.detection_callback,
            qos_profile = 10
        )

        self.cmd_vel_pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)


        self.object_search_server = ActionServer(
            self,
            action_type= SearchObject,
            action_name="search_object",
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup()
        )

        self.get_logger().info("Object Search action server started!")

    def goal_callback(self, goal_request:SearchObject.Goal):
        self.get_logger().info("Received a goal")
        #Implement some policy regarding whether to accept or reject the goal


        if goal_request.target_object in ['unknown']:
            self.get_logger().info("Goal rejected")
            return GoalResponse.REJECT
        else:
            self.get_logger().info("Goal accepted")
            return GoalResponse.ACCEPT


    def execute_callback(self, goal_handle:ServerGoalHandle):

        # Get request from goal
        target_object = goal_handle.request.target_object
        self.get_logger().info(f"Searching for: {target_object}")

        rate = self.create_rate(self.search_freq)
        start_time = self.get_clock().now()
        feedback = SearchObject.Feedback()
        result = SearchObject.Result()

        # Create rotation command
        cmd_vel_msg = TwistStamped()
        cmd_vel_msg.twist.angular.z = self.rotation_speed

        while rclpy.ok():
            elapsed_time = (self.get_clock().now() - start_time).nanoseconds / 1e9
            if self.latest_detection and \
               self.latest_detection.confidence >= self.confidence_threshold:
                
                
                result.success = True
                result.confidence = self.latest_detection.confidence
                result.message = f"Target object '{target_object}' detected with confidence {result.confidence:.3f}"
                self.stop_rotation()
                self.get_logger().info(f"Object found: {result.message}")
                goal_handle.succeed()
                return result
            
            if elapsed_time > self.max_search_time:
                self.get_logger().warn(f"Search timeout in {elapsed_time:.2f}s. Goal aborted!")
                self.stop_rotation()
                result.success = False
                result.confidence = 0.0
                result.message = f"Maximum search time reached - {elapsed_time:.2f}s"
                goal_handle.abort() 
                return result
            
            if goal_handle.is_cancel_requested:
                self.get_logger().warn("Cancelling the goal")
                self.stop_rotation()
                result.success = False
                result.message = "Goal cancelled due to client cancel request"
                result.confidence = 0.0
                goal_handle.canceled()
                return result


            
            # Continue rotating
            cmd_vel_msg.header.stamp = self.get_clock().now().to_msg()
            self.cmd_vel_pub.publish(cmd_vel_msg)
            feedback.current_velocity = cmd_vel_msg
            feedback.elapsed_time = elapsed_time
            goal_handle.publish_feedback(feedback)
            rate.sleep()
         

        # If rclpy is not ok (shutdown)
        
        result = SearchObject.Result()
        result.success = False
        result.message = "Node shutdown during search."
        result.confidence = 0.0
        self.stop_rotation()
        goal_handle.abort()
        return result
    

    def cancel_callback(self, goal_handle:ServerGoalHandle):
        self.get_logger().warn("Received a CANCEL REQUEST")
        return CancelResponse.ACCEPT 


    
    def detection_callback(self, msg):
        self.latest_detection = msg
       # self.get_logger().info(f"Detection received! Confidence: {msg.best_confidence}")


    def stop_rotation(self):
        """Publish zero velocity to stop the robot."""
        stop_msg = TwistStamped()
        stop_msg.header.stamp = self.get_clock().now().to_msg()
        stop_msg.twist.angular.z = 0.0
        self.cmd_vel_pub.publish(stop_msg)


        


def main(args=None):
    rclpy.init(args=args)
    node = ObjectSearchNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
      
    finally:
        node.destroy_node()
        rclpy.try_shutdown()



if __name__ == '__main__':
    main()
