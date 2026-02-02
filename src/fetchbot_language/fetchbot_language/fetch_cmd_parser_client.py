#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from fetchbot_interfaces.srv import ParseFetchCmd
from functools import partial
 
 
 
class FetchCmdParserClient(Node): 
    def __init__(self):
        super().__init__("fetch_cmd_parser_client")
        self.client = self.create_client(ParseFetchCmd, "parse_fetch_cmd")
        self.get_logger().info("Client is ready")



    def send_cmd_parse_request(self, user_command:str):
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Service not available, waiting...")
        self.get_logger().info("Service available!")

        request = ParseFetchCmd.Request()
        request.user_command = user_command
        future = self.client.call_async(request=request)
        future.add_done_callback(partial(self.callback_cmd_parse_request, request=request))

    def callback_cmd_parse_request(self,future,request):
        response = future.result()
        self.get_logger().info(f"Response- {response}")

 
 
def main(args=None):
    rclpy.init(args=args)
    node = FetchCmdParserClient()
    node.send_cmd_parse_request("take yellow bottle to the kitchen")
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()