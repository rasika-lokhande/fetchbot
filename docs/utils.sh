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




# MODEL PERSISTS
docker run \
  -p 5000:5000 \
  -v /home/rasika-lokhande/.cache/clip:/root/.cache/clip \
  fetchbot-vision:latest


# Reset
pkill -f gz
pkill -f ros2
rm -rf ~/.gazebo


#Test

ros2 topic pub -r 5 /detected_objects fetchbot_interfaces/msg/Detection "{
  object_names: ['blue book', 'green bottle', 'red cup', 'yellow ball'],
  confidences:  [0.42, 0.55, 0.91, 0.30],
  best_match: 'red cup',
  best_confidence: 0.91
}"


ros2 topic pub -r 5 /detected_objects fetchbot_interfaces/msg/Detection "{
  object_names: ['blue book', 'green bottle', 'red cup', 'yellow ball'],
  confidences:  [0.42, 0.55, 0.91, 0.30],
  best_match: 'blue book',
  best_confidence: 0.91
}"


ros2 run fetchbot_perception object_search_client --ros-args -p target_object:="red cup"
