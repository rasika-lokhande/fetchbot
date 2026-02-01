#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from fetchbot_interfaces.msg import Detection
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
        
        self.target_detection_publisher = self.create_publisher(msg_type=Detection,
                                                                 topic="/detected_objects",
                                                                 qos_profile=10)
        
        # Docker service URL
        self.vision_url = 'http://localhost:5000/detect'
        
        self.get_logger().info('Vision Bridge started!')
        
    
    
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
            json={'image': base64_image},
            timeout=5.0
        )
        
        # Step 5: Parse response
        result = response.json()
        
        # Step 6: Create and publish Detection message
        detection_msg = Detection()

        # Extract detections
        detections = result['detections']
        detection_msg.object_names = [d['object'] for d in detections]
        detection_msg.confidences = [d['confidence'] for d in detections]
        detection_msg.best_match = result['best_match'] if result['best_match'] else ''
        detection_msg.best_confidence = detections[0]['confidence'] if detections else 0.0

        
        self.target_detection_publisher.publish(detection_msg)
        self.get_logger().info(f'Detected: {detection_msg.best_match} ({detection_msg.best_confidence:.2f})')

        
 
 
def main(args=None):
    rclpy.init(args=args)
    node = VisionBridgeNode() # MODIFY NAME
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()