#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import MultiThreadedExecutor



from geometry_msgs.msg import TwistStamped
from fetchbot_interfaces.msg import Detection
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
        self.declare_parameter('confidence_threshold', 0.3)
        self.declare_parameter('max_search_time', 30.0)        # seconds
        self.declare_parameter('search_freq', 10.0)            # Hz

        self.rotation_speed = self.get_parameter('rotation_speed').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.max_search_time = self.get_parameter('max_search_time').value
        self.search_freq = self.get_parameter('search_freq').value
        self.latest_detection = None

        self.detection_sub = self.create_subscription(
            msg_type=Detection,
            topic='/detected_objects',
            callback = self.detection_callback,
            qos_profile = 10
        )

        self.cmd_vel_pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)


        self.object_search_server = ActionServer(
            self,
            action_type= SearchObject,
            action_name="search_object",
            execute_callback=self.execute_callback
        )

        self.get_logger().info("Object Search action server started!")

    def execute_callback(self, goal_handle:ServerGoalHandle):

        # Get request from goal
        target_object = goal_handle.request.target_object
        self.get_logger().info(f"Searching for: {target_object}")

        rate = self.create_rate(self.search_freq)
        start_time = self.get_clock().now()

        # Create rotation command
        cmd_vel_msg = TwistStamped()
        cmd_vel_msg.twist.angular.z = self.rotation_speed

        while rclpy.ok():
            elapsed_time = (self.get_clock().now() - start_time).nanoseconds / 1e9
            if self.latest_detection and \
               self.latest_detection.best_match == target_object and \
               self.latest_detection.best_confidence >= self.confidence_threshold:
                
                goal_handle.succeed()
                result = SearchObject.Result()
                result.success = True
                result.confidence = self.latest_detection.best_confidence
                result.message = f"Target object '{target_object}' detected with confidence {result.confidence:.2f}"
                self.stop_rotation()
                self.get_logger().info(f"Object found: {result.message}")
                return result
            
            # Continue rotating
            cmd_vel_msg.header.stamp = self.get_clock().now().to_msg()
            self.cmd_vel_pub.publish(cmd_vel_msg)
            rate.sleep()

        # If rclpy is not ok (shutdown)
        goal_handle.abort()
        result = SearchObject.Result()
        result.success = False
        result.message = "Node shutdown during search"
        self.stop_rotation()
        return result





    
    def detection_callback(self, msg):
        self.latest_detection = msg
       # self.get_logger().info(f"Detection received! Best match: {msg.best_match}, Confidence: {msg.best_confidence}")


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
