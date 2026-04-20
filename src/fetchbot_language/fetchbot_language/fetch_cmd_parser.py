#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from fetchbot_interfaces.srv import ParseFetchCmd
from openai import OpenAI
from pydantic import BaseModel
from fetchbot_language.system_prompt import SYSTEM_PROMPT

 
 
class FetchCmdParserNode(Node): 
    def __init__(self):
        super().__init__("fetch_cmd_parser") 


        self.openai_client = OpenAI(base_url="https://openrouter.ai/api/v1")
        self.model_name = 'openrouter/elephant-alpha'
        self.create_service(ParseFetchCmd, "parse_fetch_cmd", 
                            callback=self.parse_fetch_cmd_callback)
        
        self.get_logger().info("Parse fetch command service inititalized")

    def parse_fetch_cmd_callback(self, request, response):

        
        user_command = request.user_command

        llm_api_response = self.call_llm_api(user_command)

        response.target_object = llm_api_response.target_object
        # response.source = llm_api_response.source
        # response.destination = llm_api_response.destination
        
        return response
    

    
    
    
    def call_llm_api(self, user_prompt):

        self.get_logger().info("Calling LLM API...")

        class SearchCommand(BaseModel):
            target_object: str
            # source: str
            # destination: str

        response = self.openai_client.responses.parse(
            model= self.model_name,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            text_format=SearchCommand,)
        response = response.output_parsed
        
        self.get_logger().info("Response recieved from LLM API!")
        return response
 
 
def main(args=None):
    rclpy.init(args=args)
    node = FetchCmdParserNode() 
    #print(node.call_llm_api("i want to study"))
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()