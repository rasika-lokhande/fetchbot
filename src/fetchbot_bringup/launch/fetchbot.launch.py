from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessStart
import os




def generate_launch_description():

    tb3_gazebo_pkg = get_package_share_directory('turtlebot3_gazebo')
    nav2_bringup_pkg = get_package_share_directory('turtlebot3_navigation2')
    fetchbot_language_pkg = get_package_share_directory('fetchbot_language')
    fetchbot_perception_pkg = get_package_share_directory('fetchbot_perception')
 

    map_path = os.path.join(get_package_share_directory('fetchbot_bringup'),
                             'maps', 
                             'my_house.yaml')




    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo_pkg, 'launch', 'my_turtlebot3_house.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            # 'x_pose': '0.0',
            # 'y_pose': '0.0' #Dont use this! 
        }.items()
    )


    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                nav2_bringup_pkg,
                'launch',
                'navigation2.launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'autostart': 'true',
            'map': map_path,
            #'params_file': nav2_params
        }.items()
    )
    


    fetch_cmd_parser = Node(
    package='fetchbot_language',
    executable='fetch_cmd_parser',  
    output='screen',
    parameters=[{'use_sim_time': True}])

    vision_bridge = Node(
    package='fetchbot_perception',
    executable='vision_bridge',  
    output='screen',
    parameters=[{'use_sim_time': True}])

    object_search = Node(
    package='fetchbot_perception',
    executable='object_search',  
    output='screen',
    parameters=[{'use_sim_time': True}])

    episode_manager = Node(
    package='fetchbot_behaviours',
    executable='episode_manager',  
    output='screen',
    parameters=[{'use_sim_time': True}])

    delayed_episode_manager = TimerAction(
        period=15.0, 
        actions=[episode_manager]
    )


    # Docker container for vision
    docker_vision = ExecuteProcess(
        cmd=[
            'docker', 'run',
            '--rm',  # Remove container when it stops
            '-p', '5000:5000',
            '-v', '/home/rasika-lokhande/.cache/clip:/root/.cache/clip',
            'fetchbot-vision:latest'
        ],
        output='screen',
        shell=False
    )


    execute_task = Node(
    package='fetchbot_behaviours',
    executable='execute_task',  
    output='screen',
    parameters=[{'use_sim_time': True}])



    return LaunchDescription([
        gazebo_launch,
        nav2,
        docker_vision,
        vision_bridge,
        object_search,
        fetch_cmd_parser,
        delayed_episode_manager,
        execute_task
    ])
