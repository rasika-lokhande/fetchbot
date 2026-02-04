import rclpy.node
import py_trees
from geometry_msgs.msg import PoseStamped
from fetchbot_behaviours.types import NavGoal
import tf_transformations
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from functools import partial
from rclpy.action.client import ClientGoalHandle, GoalStatus
from rclpy.task import Future

class NavLocation(py_trees.behaviour.Behaviour):

    def __init__(self, name, node:rclpy.node.Node, nav_goal:NavGoal):
        super(NavLocation, self).__init__(name)
        self.node = node
        self.blackboard = self.attach_blackboard_client()
        self.nav_goal =  nav_goal
      
    def setup(self, **kwargs ):
        self._action_client = ActionClient(
            self.node,
            NavigateToPose,
            'navigate_to_pose')
        # Wait for action server
        self.node.get_logger().info("Waiting for navigate_to_pose action server...")
        self._action_client.wait_for_server()
        self.node.get_logger().info("Action server available!")
       
    def initialise(self):
        self.goal_pose:PoseStamped = None
        self.request_sent:bool = False
        self.goal_handle_ = None
        self.goal_future:Future = None
        self.result_future:Future = None
        self.result = None
        self.action_status = None
        pass

    def update(self):
        """
        Update method called by behavior tree on each tick.
        Manages the navigation action lifecycle.
        """
        
        # Step 1: Send navigation goal on first tick
        if not self.request_sent:
            self._send_initial_goal()
            return py_trees.common.Status.RUNNING
        
        # Step 2: Wait for goal to be accepted/rejected
        if self._is_waiting_for_goal_acceptance():
            return py_trees.common.Status.RUNNING
        
        # Step 3: Wait for navigation to complete
        if self._is_navigation_in_progress():
            return py_trees.common.Status.RUNNING
        
        # Step 4: Process final result
        return self._process_navigation_result()


    def _send_initial_goal(self):
        """Send the navigation goal to the action server."""
        self.send_nav_request()
        self.request_sent = True
        self.node.get_logger().info(
            f'Sending navigation goal to x:{self.nav_goal.pos_x}, '
            f'y:{self.nav_goal.pos_y}')


    def _is_waiting_for_goal_acceptance(self):
        """Check if we're still waiting for the goal to be accepted."""
        return self.goal_future and not self.goal_future.done()


    def _is_navigation_in_progress(self):
        """Check if navigation is still in progress."""
        return not self.result_future or not self.result_future.done()


    def _process_navigation_result(self):
        """Process the final navigation result and return appropriate status."""
        self.node.get_logger().info(f"Navigation completed with result: {self.result}")
        
        if self.action_status == GoalStatus.STATUS_SUCCEEDED:
            self.node.get_logger().info("Navigation succeeded!")
            return py_trees.common.Status.SUCCESS
        
        if self.action_status == GoalStatus.STATUS_ABORTED:
            self.node.get_logger().error("Navigation aborted")
            return py_trees.common.Status.FAILURE
        
        if self.action_status == GoalStatus.STATUS_CANCELED:
            self.node.get_logger().warning("Navigation canceled")
            return py_trees.common.Status.FAILURE
        
        # Handle unexpected status
        self.node.get_logger().warning(f"Unexpected navigation status: {self.action_status}")
        return py_trees.common.Status.FAILURE


 
    def terminate(self, new_status):
        # self.request_sent = False
        # self.node.get_logger().warn(f"{self.name} {self.status} -> {new_status}")

        # """Cancel goal if behavior is interrupted"""
        # if self.goal_handle_ is not None and new_status == py_trees.common.Status.INVALID:
        #     self.node.get_logger().warn("Canceling navigation goal...")
        #     cancel_future = self.goal_handle_.cancel_goal_async()
            
        self.request_sent = False
        self.goal_handle_ = None
        self.goal_future = None
        self.result_future = None
        self.result = None
        self.action_status = None
        self.node.get_logger().info(f"{self.name} {self.status} -> {new_status}")

    

    def send_nav_request(self):
        self.goal_pose = self.create_pose_stamped(self.nav_goal.pos_x, self.nav_goal.pos_y, self.nav_goal.rot_z)

        # Create action goal
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self.goal_pose

        #Send goal async
        self.goal_future = self._action_client.send_goal_async(goal_msg)
        self.goal_future.add_done_callback(self.goal_response_callback)


    def goal_response_callback(self,future):
        # If goal is accepted, request the result
        self.goal_handle_:ClientGoalHandle = future.result()
        if not self.goal_handle_:
            self.node.get_logger().error("Failed to get goal handle")
            return
        if self.goal_handle_.accepted:
            self.node.get_logger().info(f"Nav Goal got accepted")
            self.result_future = self.goal_handle_.get_result_async()  
            self.result_future.add_done_callback(self.goal_result_callback)
        else:
            self.node.get_logger().warn(f"Nav Goal got rejected")

    def goal_result_callback(self,future):
        #Result recieved
        result_response = future.result()
        self.result = result_response.result
        self.action_status = result_response.status
        
    
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
        
        


 

