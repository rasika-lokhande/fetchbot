import cv2
import yaml

map_img_path = '/media/rasika-lokhande/Data/RoboticsProjects/fetchbot/src/fetchbot_behaviours/fetchbot_behaviours/my_house.pgm'
map_yaml_path = '/media/rasika-lokhande/Data/RoboticsProjects/fetchbot/src/fetchbot_behaviours/fetchbot_behaviours/my_house.yaml'
class MapAnnotator:
    def __init__(self, map_image_path, map_yaml_path):
        self.image = cv2.imread(map_image_path)
        
        with open(map_yaml_path, 'r') as f:
            self.map_yaml = yaml.safe_load(f)
        
        self.resolution = self.map_yaml['resolution']
        self.origin = self.map_yaml['origin']
        self.points = {}
        self.current_room = None
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Convert pixel to world
            world_x, world_y = self.pixel_to_world(x, y)
            
            print(f"Clicked: pixel({x}, {y}) → world({world_x:.2f}, {world_y:.2f})")
            
            if self.current_room:
                if self.current_room not in self.points:
                    self.points[self.current_room] = []
                self.points[self.current_room].append((world_x, world_y))
                
                # Draw on image
                cv2.circle(self.image, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(self.image, f"{self.current_room}", 
                           (x+10, y), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0, 255, 0), 1)
                cv2.imshow('Map Annotator', self.image)
    
    def pixel_to_world(self, pixel_x, pixel_y):
        # Note: Image coordinates have y increasing downward
        # Flip y-axis for correct conversion
        height = self.image.shape[0]
        pixel_y_flipped = height - pixel_y
        
        world_x = self.origin[0] + (pixel_x * self.resolution)
        world_y = self.origin[1] + (pixel_y_flipped * self.resolution)
        
        return world_x, world_y
    
    def annotate(self):
        cv2.namedWindow('Map Annotator')
        cv2.setMouseCallback('Map Annotator', self.mouse_callback)
        cv2.imshow('Map Annotator', self.image)
        
        print("Instructions:")
        print("1. Type room name (e.g., 'kitchen') and press Enter")
        print("2. Click spawn points on the map")
        print("3. Type 'done' when finished")
        print("4. Press 'q' to quit and save")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('n'):  # New room
                room_name = input("Enter room name: ")
                self.current_room = room_name
                print(f"Now annotating: {room_name}")
        
        cv2.destroyAllWindows()
        return self.points
    
    def save_annotations(self, output_path):
        with open(output_path, 'w') as f:
            yaml.dump(self.points, f)
        print(f"Saved annotations to {output_path}")

# Usage
annotator = MapAnnotator(map_img_path, map_yaml_path)
points = annotator.annotate()
annotator.save_annotations('room_coordinates.yaml')