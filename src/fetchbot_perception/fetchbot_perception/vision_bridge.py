#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from fetchbot_interfaces.msg import ClipDetection
from fetchbot_interfaces.msg import SearchCmd
from cv_bridge import CvBridge
import cv2
import base64
import requests
import json
 
 
class VisionBridgeNode(Node): 
    def __init__(self):
        super().__init__("vision_bridge") 
        self.bridge = CvBridge()

        self.camera_subscriber = self.create_subscription(msg_type=Image,
                                                         topic="camera/image_raw",
                                                       callback=self.process_image,
                                                       qos_profile=10)
        
        self.clip_input_subscriber = self.create_subscription(msg_type=SearchCmd,
                                                         topic="/search_cmd",
                                                       callback=self.search_cmd_callback,
                                                       qos_profile=10)
        
        self.target_detection_publisher = self.create_publisher(msg_type=ClipDetection,
                                                                 topic="/detection_result",
                                                                 qos_profile=10)
        
        # Docker service URL
        self.vision_url = 'http://localhost:5000/detect'
        
        self.get_logger().info('Vision Bridge started!')

        self.search_cmd = ''
        

    def search_cmd_callback(self, search_cmd_msg):
        """Called everytime a search command message arrives"""
        self.search_cmd = search_cmd_msg.search_cmd
        #self.get_logger().info("Search command recieved - {self.search_cmd}")
    
    
    def process_image(self,img_msg):
        """Called every time a new image arrives"""
        

        # Step 1: Convert ROS Image to OpenCV format
        cv_image = self.bridge.imgmsg_to_cv2(img_msg, desired_encoding='bgr8')
        
        # Step 2: Convert to JPEG bytes
        _, jpeg_bytes = cv2.imencode('.jpg', cv_image)
        
        # Step 3: Convert to base64
        base64_image = base64.b64encode(jpeg_bytes).decode('utf-8')

        # Step 4: Call Docker vision service
        response = requests.post(
            self.vision_url,
            json={'image': base64_image, 
                  'text_input':self.search_cmd},
            timeout=5.0
        )
        
        # Step 5: Parse response
        result = response.json()
        #print(result)
       
        
        # Step 6: Create and publish Detection message
        detection_msg = ClipDetection()

        # Extract detections
        detection_result = result['result']
        #self.get_logger().info(detection_result)

        detection_msg.text_input = detection_result['text_input']
        detection_msg.confidence = detection_result['confidence']

        self.target_detection_publisher.publish(detection_msg)

        
 
 
def main(args=None):
    rclpy.init(args=args)
    node = VisionBridgeNode() 
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()