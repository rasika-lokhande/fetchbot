import rclpy.node
import py_trees
from fetchbot_interfaces.srv import ParseFetchCmd
from functools import partial



class ParseCommand(py_trees.behaviour.Behaviour):
    """Calls language service to parse command"""

    def __init__(self, name, node:rclpy.node.Node):
        super(ParseCommand, self).__init__(name)
        self.node = node
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("user_command", access=py_trees.common.Access.READ)
        self.blackboard.register_key("location", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("target_object", access=py_trees.common.Access.WRITE)
     
    def setup(self, **kwargs ):
        self.client = self.node.create_client(ParseFetchCmd, '/parse_fetch_cmd')
        self.node.get_logger().info("Parse Command Client is ready")
        
  
          
    def initialise(self):
        self.future = None
        self.response = None
        self.request_sent = False

        
    def update(self):

        #Send service request
        if not self.request_sent:
            self.user_command = self.blackboard.get("user_command")
            self.node.get_logger().info(f'User Command - {self.user_command}')
            self.send_cmd_parse_request(user_command=self.user_command)
            self.request_sent = True
            return py_trees.common.Status.RUNNING
    
        # Wait for response
        if self.future and not self.future.done():
            self.node.get_logger().info(f'User Command - {self.user_command} . RUNNING')
            return py_trees.common.Status.RUNNING
        
        # Process response
        if self.response:
            return py_trees.common.Status.SUCCESS
        else:
            self.node.get_logger().error("Command parsing failed")
            return py_trees.common.Status.FAILURE


    def terminate(self, new_status):
        self.request_sent = False  # Reset for next execution
        self.node.get_logger().warn(f"{self.name} {self.status} -> {new_status}")


    def send_cmd_parse_request(self, user_command:str):
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.node.get_logger().warn("Service not available, waiting...")
        self.node.get_logger().info("Service available!")

        self.request = ParseFetchCmd.Request()
        self.request.user_command = user_command
        self.future = self.client.call_async(request=self.request)
        self.future.add_done_callback(partial(self.callback_cmd_parse_request, request=self.request))

    def callback_cmd_parse_request(self,future,request):
        self.response = self.future.result()
        self.blackboard.set("target_object", self.response.target_object)
        self.node.get_logger().info(f"Response- {self.response}")

        
 

