# Set the model path to include TurtleBot3 models
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:/opt/ros/$ROS_DISTRO/share/turtlebot3_gazebo/models

# Now launch the world
gz sim /opt/ros/$ROS_DISTRO/share/turtlebot3_gazebo/worlds/turtlebot3_house.world



export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:/media/rasika-lokhande/Data/RoboticsProjects/fetchbot/aws-robomaker-small-house-world/models

gz sim aws-robomaker-small-house-world/worlds/small_house.world