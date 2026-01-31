ros2 run turtlebot3_teleop teleop_keyboard
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True

ros2 run nav2_map_server map_saver_cli -f maps/house
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=maps/my_house.yaml


flask --app .docker/test run --debug


# docker workflow
docker run -d -p 5000:5000 --name vision-service fetchbot-vision:latest
# Container runs in background all day

# If changes made:

# 1. Stop and remove the old container
docker stop vision-service
docker rm vision-service

# 2. Rebuild the image (fast - only code changed)
docker build -t fetchbot-vision:latest .

# 3. Run new container
docker run -d -p 5000:5000 --name vision-service fetchbot-vision:latest