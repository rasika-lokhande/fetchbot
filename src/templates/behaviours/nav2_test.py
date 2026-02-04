import rclpy.node
import py_trees
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from fetchbot_behaviours.types import NavGoal
import tf_transformations


class NavLocation(py_trees.behaviour.Behaviour):
    """Navigate to a location using Nav2 action client"""

    def __init__(self, name, node: rclpy.node.Node, nav_goal: NavGoal):
        super(NavLocation, self).__init__(name)
        self.node = node
        self.blackboard = self.attach_blackboard_client()
        self.nav_goal = nav_goal
      
    def setup(self, **kwargs):
        # Create action client instead of BasicNavigator
        self._action_client = ActionClient(
            self.node,
            NavigateToPose,
            'navigate_to_pose'
        )
        
        # Wait for action server
        self.node.get_logger().info("Waiting for navigate_to_pose action server...")
        self._action_client.wait_for_server()
        self.node.get_logger().info("Action server available!")
       
    def initialise(self):
        self.goal_handle = None
        self.result_future = None
        self.goal_sent = False

    def update(self):
        # Send goal on first update
        if not self.goal_sent:
            goal_pose = self.create_pose_stamped(
                self.nav_goal.pos_x, 
                self.nav_goal.pos_y, 
                self.nav_goal.rot_z
            )
            
            # Create action goal
            goal_msg = NavigateToPose.Goal()
            goal_msg.pose = goal_pose
            
            # Send goal asynchronously
            send_goal_future = self._action_client.send_goal_async(goal_msg)
            send_goal_future.add_done_callback(self.goal_response_callback)
            
            self.goal_sent = True
            self.node.get_logger().info(
                f'Sending navigation goal to x:{self.nav_goal.pos_x}, y:{self.nav_goal.pos_y}'
            )
            return py_trees.common.Status.RUNNING
        
        # Wait for goal to be accepted
        if self.goal_handle is None:
            return py_trees.common.Status.RUNNING
        
        # Check if we have a result
        if self.result_future is None:
            return py_trees.common.Status.RUNNING
            
        if not self.result_future.done():
            return py_trees.common.Status.RUNNING
        
        # Process result
        result = self.result_future.result()
        if result:
            self.node.get_logger().info("Navigation succeeded!")
            return py_trees.common.Status.SUCCESS
        else:
            self.node.get_logger().error("Navigation failed!")
            return py_trees.common.Status.FAILURE

    def goal_response_callback(self, future):
        """Callback when goal is accepted/rejected"""
        self.goal_handle = future.result()
        
        if not self.goal_handle.accepted:
            self.node.get_logger().error('Goal rejected!')
            return
        
        self.node.get_logger().info('Goal accepted, navigating...')
        
        # Get result future
        self.result_future = self.goal_handle.get_result_async()

    def terminate(self, new_status):
        """Cancel goal if behavior is interrupted"""
        if self.goal_handle is not None and new_status == py_trees.common.Status.INVALID:
            self.node.get_logger().warn("Canceling navigation goal...")
            cancel_future = self.goal_handle.cancel_goal_async()
            
        self.goal_sent = False
        self.goal_handle = None
        self.result_future = None
        self.node.get_logger().info(f"{self.name} {self.status} -> {new_status}")

    def create_pose_stamped(self, position_x, position_y, rotation_z):
        q_x, q_y, q_z, q_w = tf_transformations.quaternion_from_euler(0.0, 0.0, rotation_z)
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.node.get_clock().now().to_msg()
        goal_pose.pose.position.x = position_x
        goal_pose.pose.position.y = position_y
        goal_pose.pose.position.z = 0.0
        goal_pose.pose.orientation.x = q_x
        goal_pose.pose.orientation.y = q_y
        goal_pose.pose.orientation.z = q_z
        goal_pose.pose.orientation.w = q_w
        return goal_pose