from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
import os




def generate_launch_description():

    tb3_gazebo_pkg = get_package_share_directory('turtlebot3_gazebo')
    nav2_bringup_pkg = get_package_share_directory('turtlebot3_navigation2')
 

    # nav2_bringup_pkg = get_package_share_directory('nav2_bringup')

    rviz_config_path = os.path.join(
        get_package_share_directory('fetchbot_description'),
        'rviz',
        'fetchbot.rviz'
    )
    map_path = os.path.join(get_package_share_directory('fetchbot_bringup'),
                             'maps', 
                             'my_house.yaml')
    # world_path = os.path.join(get_package_share_directory('fetchbot_bringup'),
    #                             'worlds',
    #                             'test_world.sdf')
    nav2_params = os.path.join(
    get_package_share_directory('fetchbot_bringup'),
    'config',
    'nav2_params.yaml'
)



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

  



    

    # rviz = Node(
    #     package='rviz2',
    #     executable='rviz2',
    #     arguments=['-d', rviz_config_path],
    #     output='screen'
    # )


    return LaunchDescription([
        gazebo_launch,
        nav2
        #rviz
        # your nodes go here
    ])
