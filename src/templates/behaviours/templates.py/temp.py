# behaviors.py (continued)
from behaviour_base_class import RobotBehavior
import py_trees
from blackboard_keys import BlackboardKeys


class ParseCommand(RobotBehavior):
    """Calls language service to parse command"""
    
    def setup(self, **kwargs):
        self.client = self.node.create_client(ParseCommandSrv, '/parse_command')
        
    def initialise(self):
        command = self.blackboard.get(BlackboardKeys.COMMAND)
        self.request = ParseCommandSrv.Request()
        self.request.command = command
        self.future = self.client.call_async(self.request)
        
    def update(self):
        if not self.future.done():
            return py_trees.common.Status.RUNNING
            
        response = self.future.result()
        if response.success:
            # Store parsed data on blackboard
            self.blackboard.set(BlackboardKeys.TARGET_OBJECT, response.target_object)
            self.blackboard.set(BlackboardKeys.SOURCE_LOCATION, response.source_location)
            self.blackboard.set(BlackboardKeys.DEST_LOCATION, response.destination_location)
            return py_trees.common.Status.SUCCESS
        else:
            self.node.get_logger().error("Command parsing failed")
            return py_trees.common.Status.FAILURE


class NavigateToLocation(RobotBehavior):
    """Navigate to a location read from blackboard"""
    
    def __init__(self, name, node, location_key):
        super().__init__(name, node)
        self.location_key = location_key  # Which blackboard key to read
        
        # Hardcoded room coordinates (get these by driving robot around)
        self.room_coords = {
            "kitchen": (1.5, 2.0, 0.0),
            "living_room": (-1.0, 1.0, 0.0),
            "bedroom": (2.0, -1.5, 1.57),
            "bathroom": (-1.5, -1.0, 3.14)
        }
        
    def setup(self, **kwargs):
        self.nav_client = ActionClient(self.node, NavigateToPose, '/navigate_to_pose')
        
    def initialise(self):
        location_name = self.blackboard.get(self.location_key)
        x, y, yaw = self.room_coords[location_name]
        
        # Create navigation goal
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        # Set orientation from yaw...
        
        self.goal_handle = self.nav_client.send_goal_async(goal)
        
    def update(self):
        if not self.goal_handle.done():
            return py_trees.common.Status.RUNNING
            
        # Check if navigation succeeded
        result = self.goal_handle.result()
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE


class SearchForObject(RobotBehavior):
    """Call vision action to search for object"""
    
    def setup(self, **kwargs):
        self.search_client = ActionClient(self.node, SearchObject, '/search_object')
        
    def initialise(self):
        target = self.blackboard.get(BlackboardKeys.TARGET_OBJECT)
        
        goal = SearchObject.Goal()
        goal.target_object = target
        
        self.goal_handle = self.search_client.send_goal_async(goal)
        
    def update(self):
        if not self.goal_handle.done():
            return py_trees.common.Status.RUNNING
            
        result = self.goal_handle.result()
        if result.found:
            self.blackboard.set(BlackboardKeys.OBJECT_FOUND, True)
            self.blackboard.set(BlackboardKeys.OBJECT_POSITION, result.position)
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE


class SimulateGrasp(RobotBehavior):
    """Pretend to grasp object"""
    
    def initialise(self):
        self.start_time = self.node.get_clock().now()
        target = self.blackboard.get(BlackboardKeys.TARGET_OBJECT)
        self.node.get_logger().info(f"Grasping {target}...")
        
    def update(self):
        elapsed = (self.node.get_clock().now() - self.start_time).nanoseconds / 1e9
        if elapsed < 2.0:  # Simulate 2 second grasp
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.SUCCESS