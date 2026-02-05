import subprocess
import json
import rclpy
from rclpy.node import Node
import random
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
import tf_transformations

class EpisodeManager(Node):
    def __init__(self):
        super().__init__('episode_manager')
        self.get_logger().info("Episode started")
        self.object_locations = {}
        self.spawn_locations = {
        'kitchen': [(3.0,3.0)],
            'living_room': [(7.0,2.0)],
            'bedroom': [(-4.0, -1.0)],
            'office': [(7.0,-2.0)]}

        self.loc_probs = {
                    'red_cup': {
                        'kitchen': 0.6,      # Cups belong in kitchen
                        'living_room': 0.2,  # Sometimes left there
                        'bedroom': 0.15,     # Morning coffee
                        'office': 0.05
                    },
                    'blue_book': {
                        'office': 0.5,       # Study/work
                        'bedroom': 0.25,     # Reading before bed
                        'living_room': 0.15, # Coffee table
                        'kitchen': 0.1       # Recipe book?
                    },
                    'yellow_ball': {
                        'living_room': 0.5,  # Play area
                        'bedroom': 0.25,     # Kids room
                        'kitchen': 0.15,     # Rolled under table
                        'office': 0.1
                    },
                    'green_bottle': {
                        'kitchen': 0.5,      # Water bottle storage
                        'office': 0.25,      # Desk hydration
                        'bedroom': 0.15,     # Bedside
                        'living_room': 0.1
                    }
                        }


    

    def set_object(self, model_name:str, x, y,z, world_name="default"):
        # The command to call the service
        # reqtype: gz.msgs.Pose
        service_name = f"/world/{world_name}/set_pose"
        
        # We construct the request as a string that 'gz service' understands
        req_data = f'name: "{model_name}", position: {{x: {x}, y: {y}, z: {z}}}'
        
        cmd = [
            "gz", "service", "-s", service_name,
            "--reqtype", "gz.msgs.Pose",
            "--reptype", "gz.msgs.Boolean",
            "--timeout", "1000",
            "--req", req_data
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if "data: true" in result.stdout:
            print(f"Successfully moved {model_name} to ({x}, {y}, {z})")
        else:
            print(f"Failed to move model. Error: {result.stderr}")



  

    def select_object_locations(self):
        '''Function to select which location to spawn each object'''
        
        
        occupied_locations = set()  # Track which locations are already used
        
        # Draw location for each object based on their probability
        for object_name, location_probs in self.loc_probs.items():
            # Get locations and their probabilities
            locations = list(location_probs.keys())
            probabilities = list(location_probs.values())
            
            # Keep selecting until we find an unoccupied location
            selected_location = None
            while selected_location is None or selected_location in occupied_locations:
                selected_location = random.choices(locations, weights=probabilities, k=1)[0]
            
            # Mark this location as occupied
            occupied_locations.add(selected_location)
            
            # Get the spawn point from that location
            spawn_points = self.spawn_locations[selected_location]
            x, y = random.choice(spawn_points)
            
            # Store the result
            self.object_locations[object_name] = {
                'location': selected_location,
                'x': x,
                'y': y,
                'z': 0.01  # Default height
            }
            
            self.get_logger().info(f"{object_name} -> {selected_location} at ({x}, {y})")
        
        
    
    def move_all_objects(self):
        for object_name, loc_data in self.object_locations.items():
            # Transform both coordinates together
            x_g, y_g = self.transform_W_to_G(loc_data['x'], loc_data['y'])
            
            self.set_object(
                model_name=object_name,
                x=x_g,
                y=y_g,
                z=loc_data['z']
            )


    def transform_W_to_G(self, x_w, y_w):
        '''Transform coordinates from Frame W to Frame G'''
        # Translation: W origin (0, 0) is at G (-2, -0.5)
        x_g = x_w - 2.0
        y_g = y_w - 0.5
        return x_g, y_g
    
   

    def create_pose_stamped(self, navigator, position_x, position_y, rotation_z):
        q_x, q_y, q_z, q_w = tf_transformations.quaternion_from_euler(0.0, 0.0, rotation_z)
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = position_x
        goal_pose.pose.position.y = position_y
        goal_pose.pose.position.z = 0.0
        goal_pose.pose.orientation.x = q_x
        goal_pose.pose.orientation.y = q_y
        goal_pose.pose.orientation.z = q_z
        goal_pose.pose.orientation.w = q_w
        return goal_pose
        
    def set_initial_pose(self):
        nav = BasicNavigator()
        # --- Set initial pose ---
        initial_pose = self.create_pose_stamped(nav, 0.0, 0.0, 0.0)
        nav.setInitialPose(initial_pose)

    

    def start_episode(self):
        self.select_object_locations()
        self.move_all_objects()
        self.set_initial_pose()
       
            

def main(args=None):
    rclpy.init(args=args)
    node = EpisodeManager()
    
    # Start a new episode
    node.start_episode()


    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()