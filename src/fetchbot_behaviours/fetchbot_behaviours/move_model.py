import subprocess
import json

def move_model(model_name, x, y, z, world_name="default"):
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

# Example usage:

if __name__ == '__main__':
    move_model("red_cup", 5.0, 2.0, 0.1)