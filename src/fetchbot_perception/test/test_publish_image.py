import os
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
cwd = os.getcwd()

IMAGE_PATH = os.path.join(cwd, 'src/fetchbot_perception/test/test_images/yellow_bottle.jpeg')
print(IMAGE_PATH)

def main():
    rclpy.init()
    node = Node('image_tester')
    pub = node.create_publisher(Image, 'camera/image_raw', 10)
    bridge = CvBridge()

    # Load your local image
    cv_image = cv2.imread(IMAGE_PATH) 
    
    if cv_image is None:
        print("Could not find image")
        return

    msg = bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
    
    print("Publishing image... Press Ctrl+C to stop.")
    
    while rclpy.ok():
        pub.publish(msg)
        rclpy.spin_once(node, timeout_sec=1.0)

if __name__ == '__main__':
    main()