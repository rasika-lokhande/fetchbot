from behaviour_base_class import RobotBehavior
import py_trees
from blackboard_keys import BlackboardKeys
from fetchbot_interfaces.srv import ParseFetchCmd


class ParseCommand(RobotBehavior):
    """Calls language service to parse command"""
    
    def setup(self, **kwargs):
        self.client = self.node.create_client(ParseFetchCmd, '/parse_fetch_cmd')
        self.get_logger().info("Parse Command Client is ready")

        
    def initialise(self):
        command = self.blackboard.get(BlackboardKeys.COMMAND)
        self.request = ParseFetchCmd.Request()
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
